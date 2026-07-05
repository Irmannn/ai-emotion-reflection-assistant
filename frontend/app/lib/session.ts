const SESSION_KEY = "emotion_reflection_session_id";

export function getOrCreateSessionId(): string {
  const existingSessionId = window.localStorage.getItem(SESSION_KEY);
  if (existingSessionId) {
    return existingSessionId;
  }

  const sessionId = crypto.randomUUID();
  window.localStorage.setItem(SESSION_KEY, sessionId);
  return sessionId;
}
