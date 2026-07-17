"use client";

import { FormEvent, useState } from "react";

import type { AgentChatResponse } from "../types/reflection";

type AgentPanelProps = {
  disabled: boolean;
  isRunning: boolean;
  result: AgentChatResponse | null;
  onSubmit: (message: string) => Promise<void>;
};

const EXAMPLE_PROMPTS = [
  "帮我找出最近和焦虑有关的复盘，并总结共同触发点。",
  "基于我最近的复盘，给我一个本周可执行的三步行动计划。"
];

export function AgentPanel({ disabled, isRunning, result, onSubmit }: AgentPanelProps) {
  const [message, setMessage] = useState(EXAMPLE_PROMPTS[0]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedMessage = message.trim();
    if (!trimmedMessage) {
      return;
    }
    await onSubmit(trimmedMessage);
  }

  return (
    <section className="rounded-[2rem] border border-emerald-100 bg-white/80 p-6 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-sage">Agent / Tool Calling</p>
          <h2 className="mt-2 text-2xl font-bold">AI 行动助手</h2>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">
            用自然语言让 AI 查询你的历史复盘。当前版本只开放只读工具，不会删除或修改数据。
          </p>
        </div>
        <span className="rounded-full bg-calm px-3 py-1 text-xs font-semibold text-sage">Stage 7</span>
      </div>

      <form onSubmit={handleSubmit} className="mt-5 grid gap-3">
        <textarea
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          rows={3}
          className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm leading-6 outline-none transition focus:border-sage focus:ring-4 focus:ring-emerald-100"
          placeholder="例如：帮我回顾最近几次焦虑相关复盘，并整理行动建议。"
        />
        <div className="flex flex-wrap items-center gap-3">
          <button
            type="submit"
            disabled={disabled || isRunning}
            className="rounded-full bg-ink px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isRunning ? "Agent 分析中..." : "运行 Agent"}
          </button>
          {EXAMPLE_PROMPTS.map((prompt) => (
            <button
              key={prompt}
              type="button"
              onClick={() => setMessage(prompt)}
              className="rounded-full border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-600 transition hover:border-sage hover:text-sage"
            >
              {prompt}
            </button>
          ))}
        </div>
      </form>

      {result ? (
        <div className="mt-5 grid gap-4">
          <div className="rounded-2xl bg-white p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Agent 回答</p>
            <p className="mt-2 whitespace-pre-wrap text-sm leading-7 text-slate-700">{result.answer}</p>
          </div>
          <div className="rounded-2xl bg-white p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">工具调用</p>
            {result.tool_calls.length ? (
              <div className="mt-3 grid gap-3">
                {result.tool_calls.map((toolCall, index) => (
                  <div key={`${toolCall.tool_name}-${index}`} className="rounded-xl border border-slate-100 bg-slate-50 p-3 text-sm">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="rounded-full bg-white px-2 py-1 text-xs font-semibold text-sage">Tool {index + 1}</span>
                      <span className="font-semibold text-ink">{toolCall.tool_name}</span>
                      <span className="text-xs text-slate-500">{toolCall.status}</span>
                    </div>
                    <p className="mt-2 text-slate-600">{toolCall.result_summary}</p>
                    {toolCall.error_message ? <p className="mt-2 text-xs text-red-600">{toolCall.error_message}</p> : null}
                  </div>
                ))}
              </div>
            ) : (
              <p className="mt-2 text-sm text-slate-500">本次没有调用工具，模型直接回答。</p>
            )}
          </div>
        </div>
      ) : null}
    </section>
  );
}

