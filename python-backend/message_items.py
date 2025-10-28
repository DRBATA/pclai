"""Local definitions for conversation input items.

The upstream `openai-agents` package no longer exposes `MessageInputItem`,
but our codebase still expects it.  This minimal version preserves the fields
we actually use (``role`` and ``content``) while remaining fully compatible
with Pydantic validation and `model_dump()` output.

If you later need more advanced behaviour (e.g., metadata, status fields),
you can safely extend this model without changing the public interface.
"""
from typing import Literal, List, Dict, Any, Union

from pydantic import BaseModel, Field


class MessageInputItem(BaseModel):
    """Represents a single user / system message fed *into* the agent runner.

    Only two attributes are currently required by ``api.py``:
      • ``role``   – "user", "system", or "developer" (defaults to "user")
      • ``content`` – either a raw string or a list/dict structure accepted by
        OpenAI's Responses API.  We keep this flexible via ``Union``.
    """

    role: Literal["user", "system", "developer"] = Field("user", description="Message role recognised by the Runner")
    content: Union[str, List[Dict[str, Any]]] = Field(..., description="Message content; plain text or rich content list")

    model_config = {
        "extra": "forbid",
        "populate_by_name": True,
    }
