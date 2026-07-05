import type { CreateReflectionPayload, ReflectionDetail, ReflectionListItem } from "../types/reflection";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers
    }
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function createReflection(payload: CreateReflectionPayload): Promise<ReflectionDetail> {
  return request<ReflectionDetail>("/api/reflections", {
    method: "POST",
    body: JSON.stringify(payload)
  });
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
