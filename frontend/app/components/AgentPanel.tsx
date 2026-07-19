"use client";

import { FormEvent, useState } from "react";

import type { AgentConversation, AgentMessage, AgentToolCall } from "../types/reflection";

type AgentPanelProps = {
  disabled: boolean;
  isLoading: boolean;
  isStreaming: boolean;
  conversations: AgentConversation[];
  selectedConversationId: string | null;
  messages: AgentMessage[];
  error: string;
  onNewConversation: () => void;
  onSelectConversation: (conversationId: string) => void;
  onSubmit: (message: string) => Promise<boolean>;
};

const EXAMPLE_PROMPTS = [
  "帮我找出最近和焦虑有关的复盘，并总结共同触发点。",
  "基于我最近的复盘，给我一个本周可执行的三步行动计划。"
];

export function AgentPanel({
  disabled,
  isLoading,
  isStreaming,
  conversations,
  selectedConversationId,
  messages,
  error,
  onNewConversation,
  onSelectConversation,
  onSubmit
}: AgentPanelProps) {
  const [message, setMessage] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedMessage = message.trim();
    if (!trimmedMessage) {
      return;
    }
    const didSend = await onSubmit(trimmedMessage);
    if (didSend) {
      setMessage("");
    }
  }

  return (
    <section className="overflow-hidden rounded-[2rem] border border-emerald-100 bg-white/80 shadow-sm">
      <div className="border-b border-emerald-100 bg-white/70 px-6 py-5">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-sage">Stage 8 / Stateful Agent</p>
            <h2 className="mt-2 text-2xl font-bold">AI 行动助手</h2>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              对话会保存到后端。Agent 会结合当前会话的最近消息，必要时查询你的历史复盘。
            </p>
          </div>
          <span className="rounded-full bg-calm px-3 py-1 text-xs font-semibold text-sage">SSE Streaming</span>
        </div>
      </div>

      <div className="grid min-h-[34rem] lg:grid-cols-[15rem_1fr]">
        <aside className="border-b border-emerald-100 bg-emerald-50/40 p-4 lg:border-b-0 lg:border-r">
          <button
            type="button"
            onClick={onNewConversation}
            disabled={disabled || isStreaming}
            className="w-full rounded-xl border border-sage bg-white px-3 py-2.5 text-sm font-semibold text-sage transition hover:bg-emerald-50 disabled:cursor-not-allowed disabled:opacity-60"
          >
            + 新建对话
          </button>
          <p className="mt-5 text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">最近对话</p>
          <div className="mt-3 flex gap-2 overflow-x-auto lg:flex-col lg:overflow-visible">
            {isLoading ? <p className="px-2 py-3 text-xs text-slate-500">正在读取会话...</p> : null}
            {!isLoading && conversations.length === 0 ? (
              <p className="px-2 py-3 text-xs leading-5 text-slate-500">发送第一条消息后，会话会保存在这里。</p>
            ) : null}
            {conversations.map((conversation) => (
              <button
                key={conversation.id}
                type="button"
                onClick={() => onSelectConversation(conversation.id)}
                disabled={isStreaming}
                className={`min-w-40 rounded-xl px-3 py-2.5 text-left text-sm transition lg:min-w-0 ${
                  selectedConversationId === conversation.id
                    ? "bg-white font-semibold text-ink shadow-sm"
                    : "text-slate-600 hover:bg-white/70"
                } disabled:cursor-not-allowed disabled:opacity-60`}
              >
                <span className="block truncate">{conversation.title}</span>
              </button>
            ))}
          </div>
        </aside>

        <div className="flex min-w-0 flex-col">
          <div className="flex-1 space-y-4 overflow-y-auto p-5">
            {selectedConversationId === null && messages.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-emerald-200 bg-emerald-50/50 p-5 text-sm leading-6 text-slate-600">
                新建一个上下文独立的对话，或直接在下方输入问题开始。第一条消息发送后会自动创建会话。
              </div>
            ) : null}
            {messages.map((item) => (
              <MessageBubble key={item.id} message={item} />
            ))}
          </div>

          <div className="border-t border-emerald-100 bg-white/80 p-5">
            {error ? <p className="mb-3 rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
            <form onSubmit={handleSubmit} className="grid gap-3">
              <textarea
                value={message}
                onChange={(event) => setMessage(event.target.value)}
                rows={3}
                disabled={disabled || isStreaming}
                className="w-full resize-none rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm leading-6 outline-none transition focus:border-sage focus:ring-4 focus:ring-emerald-100 disabled:bg-slate-50"
                placeholder="例如：帮我回顾最近几次焦虑相关复盘，并整理行动建议。"
              />
              <div className="flex flex-wrap items-center gap-3">
                <button
                  type="submit"
                  disabled={disabled || isStreaming || !message.trim()}
                  className="rounded-full bg-ink px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {isStreaming ? "Agent 回复中..." : "发送消息"}
                </button>
                {!message.trim() && !isStreaming
                  ? EXAMPLE_PROMPTS.map((prompt) => (
                      <button
                        key={prompt}
                        type="button"
                        onClick={() => setMessage(prompt)}
                        disabled={disabled}
                        className="rounded-full border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-600 transition hover:border-sage hover:text-sage"
                      >
                        {prompt}
                      </button>
                    ))
                  : null}
              </div>
            </form>
          </div>
        </div>
      </div>
    </section>
  );
}

function MessageBubble({ message }: { message: AgentMessage }) {
  const isUser = message.role === "user";
  return (
    <article className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[88%] rounded-2xl px-4 py-3 text-sm leading-7 ${
          isUser ? "bg-ink text-white" : "border border-slate-100 bg-white text-slate-700 shadow-sm"
        }`}
      >
        <p className={`text-xs font-semibold ${isUser ? "text-slate-300" : "text-sage"}`}>
          {isUser ? "你" : "AI 行动助手"}
        </p>
        {message.content ? <p className="mt-1 whitespace-pre-wrap">{message.content}</p> : null}
        {!isUser && message.status === "pending" ? <p className="mt-2 text-xs text-slate-400">正在思考并生成回答...</p> : null}
        {!isUser && message.status === "failed" ? (
          <p className="mt-2 text-xs text-red-600">{message.error_message ?? "本次回答失败，请保留输入后手动重试。"}</p>
        ) : null}
        {!isUser && message.tool_calls.length ? (
          <div className="mt-3 grid gap-2 border-t border-slate-100 pt-3">
            <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">工具调用</p>
            {message.tool_calls.map((toolCall, index) => (
              <ToolCallItem key={`${toolCall.tool_name}-${index}`} toolCall={toolCall} />
            ))}
          </div>
        ) : null}
        {!isUser && message.duration_ms !== null ? (
          <p className="mt-3 text-xs text-slate-400">耗时 {(message.duration_ms / 1000).toFixed(1)} 秒</p>
        ) : null}
      </div>
    </article>
  );
}

function ToolCallItem({ toolCall }: { toolCall: AgentToolCall }) {
  const isRunning = toolCall.status === "running";
  return (
    <div className="rounded-xl bg-slate-50 px-3 py-2 text-xs text-slate-600">
      <span className="font-semibold text-ink">{toolCall.tool_name}</span>
      <span className="ml-2 text-slate-400">{isRunning ? "执行中..." : toolCall.status}</span>
      {!isRunning ? <p className="mt-1">{toolCall.result_summary}</p> : null}
      {toolCall.error_message ? <p className="mt-1 text-red-600">{toolCall.error_message}</p> : null}
    </div>
  );
}
