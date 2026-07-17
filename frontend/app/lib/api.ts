import type {
  AgentChatResponse,
  CreateReflectionPayload,
  ReflectionDetail,
  ReflectionListItem,
  StreamCreateReflectionResult
} from "../types/reflection";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type StreamCreateReflectionHandlers = {
  onDelta: (content: string) => void;
};

type StreamEventMessage = {
  event: string;
  data: string;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers
    }
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
  }

  return response.json() as Promise<T>;
}

export function createReflection(payload: CreateReflectionPayload): Promise<ReflectionDetail> {
  return request<ReflectionDetail>("/api/reflections", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function streamCreateReflection(
  payload: CreateReflectionPayload,
  handlers: StreamCreateReflectionHandlers
): Promise<StreamCreateReflectionResult> {
  const response = await fetch(`${API_BASE_URL}/api/reflections/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
  }

  if (!response.body) {
    throw new Error("当前浏览器不支持读取流式响应。");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let result: StreamCreateReflectionResult | null = null;

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const messages = buffer.split("\n\n");
    buffer = messages.pop() ?? "";

    for (const message of messages) {
      const nextResult = handleStreamMessage(message, handlers);
      if (nextResult) {
        result = nextResult;
      }
    }
  }

  buffer += decoder.decode();
  if (buffer.trim()) {
    const nextResult = handleStreamMessage(buffer, handlers);
    if (nextResult) {
      result = nextResult;
    }
  }

  if (!result) {
    throw new Error("流式生成已结束，但后端没有返回保存后的记录 ID。");
  }

  return result;
}

export function listReflections(sessionId: string): Promise<ReflectionListItem[]> {
  const params = new URLSearchParams({ session_id: sessionId });
  return request<ReflectionListItem[]>(`/api/reflections?${params.toString()}`);
}

export function getReflection(recordId: number, sessionId: string): Promise<ReflectionDetail> {
  const params = new URLSearchParams({ session_id: sessionId });
  return request<ReflectionDetail>(`/api/reflections/${recordId}?${params.toString()}`);
}

export function deleteReflection(recordId: number, sessionId: string): Promise<{ deleted: boolean }> {
  const params = new URLSearchParams({ session_id: sessionId });
  return request<{ deleted: boolean }>(`/api/reflections/${recordId}?${params.toString()}`, {
    method: "DELETE"
  });
}

export function chatWithAgent(sessionId: string, message: string): Promise<AgentChatResponse> {
  return request<AgentChatResponse>("/api/agent/chat", {
    method: "POST",
    body: JSON.stringify({
      session_id: sessionId,
      message
    })
  });
}

async function readErrorMessage(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as { detail?: string };
    return data.detail ?? `Request failed: ${response.status}`;
  } catch {
    return `Request failed: ${response.status}`;
  }
}

function handleStreamMessage(
  rawMessage: string,
  handlers: StreamCreateReflectionHandlers
): StreamCreateReflectionResult | null {
  const message = parseStreamMessage(rawMessage);
  if (!message) {
    return null;
  }

  if (message.event === "delta") {
    const data = JSON.parse(message.data) as { content?: string };
    if (data.content) {
      handlers.onDelta(data.content);
    }
    return null;
  }

  if (message.event === "done") {
    return JSON.parse(message.data) as StreamCreateReflectionResult;
  }

  if (message.event === "error") {
    const data = JSON.parse(message.data) as { message?: string };
    throw new Error(data.message ?? "流式生成失败。");
  }

  return null;
}

function parseStreamMessage(rawMessage: string): StreamEventMessage | null {
  const lines = rawMessage.split("\n");
  let event = "message";
  const dataLines: string[] = [];

  for (const line of lines) {
    if (line.startsWith("event:")) {
      event = line.slice("event:".length).trim();
    }

    if (line.startsWith("data:")) {
      dataLines.push(line.slice("data:".length).trimStart());
    }
  }

  if (dataLines.length === 0) {
    return null;
  }

  return {
    event,
    data: dataLines.join("\n")
  };
}
