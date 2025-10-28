"use client";

import { PanelSection } from "./panel-section";
import { Card, CardContent } from "@/components/ui/card";
import { BookText } from "lucide-react";

interface ConversationContextProps {
  context: {
    symptoms?: string;                           // Host Agent collects
    possible_conditions?: string;                // Scout Agent determines
    calculators?: Record<string, any>;           // Librarian Agent calculates with tool 
    differential_probabilities?: Record<string, number>; // PI analysis of risks with Bayesian inference
    relevant_red_flags_absent?: string[];        // Safety check from all agents
    safety_concerns?: Array<{                    // Tracked safety concerns with agent analyses
      id: string;                                // Concern identifier
      title: string;                             // Brief title
      severity: number;                          // 1-5 scale
      agent_analysis: string;                    // Clinical reasoning
      assessment_status: string;                 // pending/reviewed/cleared/escalated
      reviewed_by: string[];                     // Agents who reviewed
    }>;
    safety_clinical_assessment?: string;         // Collaborative safety assessment
    escalation_advice?: string;                  // Explains what should happen and escalation guidelines
    recommended_options?: string[];              // Maître d' Agent provides ideal combinations
    contraindication_checker?: string[];         // Medication reviews and safety checks
    account_number?: string;                     // System use
  };
}

export function ConversationContext({ context }: ConversationContextProps) {
  return (
    <PanelSection
      title="Conversation Context"
      icon={<BookText className="h-4 w-4 text-blue-600" />}
    >
      <Card className="bg-gradient-to-r from-white to-gray-50 border-gray-200 shadow-sm">
        <CardContent className="p-3">
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(context).map(([key, value]) => (
              <div
                key={key}
                className="flex items-center gap-2 bg-white p-2 rounded-md border border-gray-200 shadow-sm transition-all"
              >
                <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                <div className="text-xs">
                  <span className="text-zinc-500 font-light">{key}:</span>{" "}
                  <span
                    className={
                      value
                        ? "text-zinc-900 font-light"
                        : "text-gray-400 italic"
                    }
                  >
                    {typeof value === 'object' ? JSON.stringify(value) : value || "null"}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </PanelSection>
  );
}