export type FocusArea = "情绪理解" | "认知偏差" | "人际关系" | "行动建议" | "综合分析";

export type ReflectionFormValues = {
  event_text: string;
  emotion_tags: string[];
  emotion_intensity: number;
  automatic_thoughts: string;
  body_reaction: string;
  focus_area: FocusArea;
};

export type CreateReflectionPayload = ReflectionFormValues & {
  session_id: string;
};

export type ReflectionListItem = {
  id: number;
  event_summary: string;
  emotion_tags: string;
  emotion_intensity: number;
  feedback: string | null;
  created_at: string;
};

export type KnowledgeReference = {
  source: string;
  title: string;
  content_preview: string;
  score: number;
};

export type ReflectionDetail = {
  id: number;
  session_id: string;
  event_text: string;
  emotion_tags: string;
  emotion_intensity: number;
  automatic_thoughts: string;
  body_reaction: string;
  focus_area: string;
  ai_report: string;
  feedback: string | null;
  created_at: string;
  updated_at: string;
  references: KnowledgeReference[];
};

export type StreamCreateReflectionResult = {
  record_id: number;
};

export type AgentToolCall = {
  tool_name: string;
  arguments: Record<string, unknown>;
  result_summary: string;
  status: string;
  error_message: string | null;
};

export type AgentChatResponse = {
  answer: string;
  tool_calls: AgentToolCall[];
};
