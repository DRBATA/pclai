from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import uuid4
import time
import logging

from main import (
    HostAgent,
    PIAgent,
    GraphReasoningAgent,
    RecommendationAgent,
    create_initial_context,
)

from agents import (
    Runner,
    ItemHelpers,
    MessageOutputItem,
    HandoffOutputItem,
    ToolCallItem,
    ToolCallOutputItem,
    InputGuardrailTripwireTriggered,
    Handoff,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS configuration (adjust as needed for deployment)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Models
# =========================

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str

class MessageResponse(BaseModel):
    content: str
    agent: str

class AgentEvent(BaseModel):
    id: str
    type: str
    agent: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[float] = None

class GuardrailCheck(BaseModel):
    id: str
    name: str
    input: str
    reasoning: str
    passed: bool
    timestamp: float

class ChatResponse(BaseModel):
    conversation_id: str
    current_agent: str
    messages: List[MessageResponse]
    events: List[AgentEvent]
    context: Dict[str, Any]
    agents: List[Dict[str, Any]]
    guardrails: List[GuardrailCheck] = []

# =========================
# In-memory store for conversation state
# =========================

class ConversationStore:
    def get(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        pass

    def save(self, conversation_id: str, state: Dict[str, Any]):
        pass

class InMemoryConversationStore(ConversationStore):
    _conversations: Dict[str, Dict[str, Any]] = {}

    def get(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        return self._conversations.get(conversation_id)

    def save(self, conversation_id: str, state: Dict[str, Any]):
        self._conversations[conversation_id] = state

# TODO: when deploying this app in scale, switch to your own production-ready implementation
conversation_store = InMemoryConversationStore()

# =========================
# Helpers
# =========================

def _resolve_agent(agent_name: str):
    """Return the agent instance that matches the given name."""
    if agent_name == HostAgent.name:
        return HostAgent
    if agent_name == PIAgent.name:
        return PIAgent
    if agent_name == GraphReasoningAgent.name:
        return GraphReasoningAgent
    if agent_name == RecommendationAgent.name:
        return RecommendationAgent
    # Fallback to host agent if unknown
    return HostAgent

def _get_agent_by_name(name: str):
    """Return the agent object by name."""
    agents = {
        HostAgent.name: HostAgent,
        PIAgent.name: PIAgent,
        GraphReasoningAgent.name: GraphReasoningAgent,
        RecommendationAgent.name: RecommendationAgent,
    }
    return agents.get(name, HostAgent)

def _get_guardrail_name(g) -> str:
    """Extract a friendly guardrail name."""
    name_attr = getattr(g, "name", None)
    if isinstance(name_attr, str) and name_attr:
        return name_attr
    guard_fn = getattr(g, "guardrail_function", None)
    if guard_fn is not None and hasattr(guard_fn, "__name__"):
        return guard_fn.__name__.replace("_", " ").title()
    fn_name = getattr(g, "__name__", None)
    if isinstance(fn_name, str) and fn_name:
        return fn_name.replace("_", " ").title()
    return str(g)

def _build_agents_list() -> List[Dict[str, Any]]:
    """Build a list of all available agents and their metadata."""
    def make_agent_dict(agent):
        return {
            "name": agent.name,
            "description": getattr(agent, "handoff_description", ""),
            "handoffs": [getattr(h, "agent_name", getattr(h, "name", "")) for h in getattr(agent, "handoffs", [])],
            "tools": [getattr(t, "name", getattr(t, "__name__", "")) for t in getattr(agent, "tools", [])],
            "input_guardrails": [_get_guardrail_name(g) for g in getattr(agent, "input_guardrails", [])],
        }
    return [
        make_agent_dict(HostAgent),
        make_agent_dict(PIAgent),
        make_agent_dict(GraphReasoningAgent),
        make_agent_dict(RecommendationAgent),
    ]

# =========================
# Main Chat Endpoint
# =========================

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """
    Main chat endpoint for agent orchestration.
    Handles conversation state, agent routing, and guardrail checks.
    """
    # Initialize or retrieve conversation state
    is_new = not req.conversation_id or conversation_store.get(req.conversation_id) is None
    if is_new:
        conversation_id: str = uuid4().hex
        ctx = create_initial_context()
        current_agent_name = HostAgent.name
        state: Dict[str, Any] = {
            "input_items": [],
            "context": ctx,
            "current_agent": current_agent_name,
        }
        # If empty message on new conversation, trigger agent to send greeting
        if req.message.strip() == "":
            # Add a special trigger message to get the agent to greet
            state["input_items"].append({"role": "user", "content": "[START_CONVERSATION]"})
        else:
            state["input_items"].append({"role": "user", "content": req.message})
    else:
        conversation_id = req.conversation_id  # type: ignore
        state = conversation_store.get(conversation_id)
        # Add the user's message to the history as a dict (SDK handles dicts fine)
        state["input_items"].append({"role": "user", "content": req.message})

    # Ensure current_agent is properly resolved
    current_agent_name = state.get("current_agent", HostAgent.name)
    current_agent = _resolve_agent(current_agent_name)
    # Save the current agent name in state (in case it was defaulted)
    state["current_agent"] = current_agent.name
    # Save the updated state back to the store
    conversation_store.save(conversation_id, state)
    
    old_context = state["context"].model_dump().copy()
    guardrail_checks: List[GuardrailCheck] = []

    # Keep running agents until no more handoffs occur
    all_results = []  # Accumulate all results
    max_handoffs = 10  # Prevent infinite loops
    handoff_count = 0
    
    while handoff_count < max_handoffs:
        try:
            result = await Runner.run(current_agent, state["input_items"], context=state["context"])
            all_results.append(result)  # Store each result
            # Context is modified by reference, no need to extract it
        except InputGuardrailTripwireTriggered as e:
            failed = e.guardrail_result.guardrail
            gr_output = e.guardrail_result.output.output_info
            gr_reasoning = getattr(gr_output, "reasoning", "")
            gr_input = req.message
            gr_timestamp = time.time() * 1000
            for g in current_agent.input_guardrails:
                guardrail_checks.append(GuardrailCheck(
                    id=uuid4().hex,
                    name=_get_guardrail_name(g),
                    input=gr_input,
                    reasoning=(gr_reasoning if g == failed else ""),
                    passed=(g != failed),
                    timestamp=gr_timestamp,
                ))
            refusal = "Sorry, I can only help with questions related to your health symptoms and over-the-counter medication options."
            state["input_items"].append({"role": "assistant", "content": refusal})
            return ChatResponse(
                conversation_id=conversation_id,
                current_agent=current_agent.name,
                messages=[MessageResponse(content=refusal, agent=current_agent.name)],
                events=[],
                context=state["context"].model_dump(),
                agents=_build_agents_list(),
                guardrails=guardrail_checks,
            )
        
        # Don't pass full history - agents only need latest user message + context
        # The context already has the structured summary (age, symptoms, etc.)
        # We'll keep the original user message for the next agent
        pass
        
        # Check if there's a handoff in the result
        has_handoff = any(isinstance(item, HandoffOutputItem) for item in result.new_items)
        if has_handoff:
            # Find the target agent and continue the loop
            for item in result.new_items:
                if isinstance(item, HandoffOutputItem):
                    current_agent = item.target_agent
                    state["current_agent"] = current_agent.name
                    handoff_count += 1
                    # Don't clear input_items - keep conversation flowing
                    # The agent will start working based on context
                    break
        else:
            # No handoff, break the loop
            break

    messages: List[MessageResponse] = []
    events: List[AgentEvent] = []

    # Keep track of the active agent for this response
    active_agent_name = current_agent.name
    
    # Process ALL accumulated results
    logger.info(f"Processing {len(all_results)} agent results")
    for result in all_results:
        logger.info(f"Result has {len(result.new_items)} items")
        for item in result.new_items:
            if isinstance(item, MessageOutputItem):
                text = ItemHelpers.text_message_output(item)
                logger.info(f"Message from {item.agent.name}: {text[:100]}")
                messages.append(MessageResponse(content=text, agent=item.agent.name))
                events.append(AgentEvent(id=uuid4().hex, type="message", agent=item.agent.name, content=text))
            # Handle handoff output and agent switching
            elif isinstance(item, HandoffOutputItem):
                # Record the handoff event
                events.append(
                    AgentEvent(
                        id=uuid4().hex,
                        type="handoff",
                        agent=item.source_agent.name,
                        content=f"{item.source_agent.name} -> {item.target_agent.name}",
                        metadata={"source_agent": item.source_agent.name, "target_agent": item.target_agent.name},
                    )
                )
                # If there is an on_handoff callback defined for this handoff, show it as a tool call
                from_agent = item.source_agent
                to_agent = item.target_agent
                # Find the Handoff object on the source agent matching the target
                ho = next(
                    (h for h in getattr(from_agent, "handoffs", [])
                     if isinstance(h, Handoff) and getattr(h, "agent_name", None) == to_agent.name),
                    None,
                )
                if ho:
                    fn = ho.on_invoke_handoff
                    fv = fn.__code__.co_freevars
                    cl = fn.__closure__ or []
                    if "on_handoff" in fv:
                        idx = fv.index("on_handoff")
                        if idx < len(cl) and cl[idx].cell_contents:
                            cb = cl[idx].cell_contents
                            cb_name = getattr(cb, "__name__", repr(cb))
                            events.append(
                                AgentEvent(
                                    id=uuid4().hex,
                                    type="tool_call",
                                    agent=to_agent.name,
                                    content=cb_name,
                                )
                            )
                current_agent = item.target_agent
                # Update state with new agent name to ensure persistence
                state["current_agent"] = current_agent.name
            elif isinstance(item, ToolCallItem):
                tool_name = getattr(item.raw_item, "name", None)
                raw_args = getattr(item.raw_item, "arguments", None)
                tool_args: Any = raw_args
                if isinstance(raw_args, str):
                    try:
                        import json
                        tool_args = json.loads(raw_args)
                    except Exception:
                        pass
                events.append(
                    AgentEvent(
                        id=uuid4().hex,
                        type="tool_call",
                        agent=item.agent.name,
                        content=tool_name or "",
                        metadata={"tool_args": tool_args},
                    )
                )
                # If the tool is display_seat_map, send a special message so the UI can render the seat selector.
                if tool_name == "display_seat_map":
                    messages.append(
                        MessageResponse(
                            content="DISPLAY_SEAT_MAP",
                            agent=item.agent.name,
                        )
                    )
            elif isinstance(item, ToolCallOutputItem):
                events.append(
                    AgentEvent(
                        id=uuid4().hex,
                        type="tool_output",
                        agent=item.agent.name,
                        content=str(item.output),
                        metadata={"tool_result": item.output},
                    )
                )

    # Get the latest context for response
    try:
        # Try to use model_dump first (newer Pydantic)
        new_context = state["context"].model_dump()
    except AttributeError:
        # Fall back to dict() for older Pydantic versions
        new_context = state["context"].dict()

    # Update state with current active agent
    state["current_agent"] = active_agent_name
    conversation_store.save(conversation_id, state)

    # Show differences in context
    context_changes = []
    for key in new_context:
        if key not in old_context or new_context[key] != old_context[key]:
            context_changes.append(key)

    if context_changes:
        events.append(
            AgentEvent(
                id=uuid4().hex,
                type="context_update",
                agent=active_agent_name,
                content="",
                metadata={"changes": context_changes},
            )
        )

    # Build input list excluding handoff items, then serialize
    filtered_inputs = [
        item for item in result.to_input_list() if not isinstance(item, HandoffOutputItem)
    ]
    state["input_items"] = [
        item.model_dump() if hasattr(item, 'model_dump') else 
        (item.dict() if hasattr(item, 'dict') else item) 
        for item in filtered_inputs
    ]
    conversation_store.save(conversation_id, state)

    # Build guardrail results: mark failures (if any), and any others as passed
    final_guardrails: List[GuardrailCheck] = []
    for g in getattr(current_agent, "input_guardrails", []):
        name = _get_guardrail_name(g)
        failed = next((gc for gc in guardrail_checks if gc.name == name), None)
        if failed:
            final_guardrails.append(failed)
        else:
            final_guardrails.append(GuardrailCheck(
                id=uuid4().hex,
                name=name,
                input=req.message,
                reasoning="",
                passed=True,
                timestamp=time.time() * 1000,
            ))

    return ChatResponse(
        conversation_id=conversation_id,
        current_agent=active_agent_name,  # Use the final active agent name
        messages=messages,
        events=events,
        context=new_context,
        agents=_build_agents_list(),
        guardrails=guardrail_checks,
    )
