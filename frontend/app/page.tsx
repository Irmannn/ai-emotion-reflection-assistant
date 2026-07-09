"use client";

import { useEffect, useState } from "react";

import { HistoryList } from "./components/HistoryList";
import { ReflectionDetail } from "./components/ReflectionDetail";
import { ReflectionForm } from "./components/ReflectionForm";
import { deleteReflection, getReflection, listReflections, streamCreateReflection } from "./lib/api";
import { getOrCreateSessionId } from "./lib/session";
import type { ReflectionDetail as ReflectionDetailType, ReflectionFormValues, ReflectionListItem } from "./types/reflection";

export default function Home() {
  const [sessionId, setSessionId] = useState("");
  const [records, setRecords] = useState<ReflectionListItem[]>([]);
  const [selectedRecord, setSelectedRecord] = useState<ReflectionDetailType | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [streamingReport, setStreamingReport] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const nextSessionId = getOrCreateSessionId();
    setSessionId(nextSessionId);
    void loadRecords(nextSessionId);
  }, []);

  async function loadRecords(nextSessionId = sessionId) {
    if (!nextSessionId) {
      return;
    }

    setIsLoading(true);
    setError("");
    try {
      const nextRecords = await listReflections(nextSessionId);
      setRecords(nextRecords);
    } catch {
      setError("历史记录加载失败，请确认后端服务已启动。");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleCreateReflection(values: ReflectionFormValues) {
    if (!sessionId) {
      setError("session_id 尚未初始化，请刷新页面重试。");
      return false;
    }

    setIsSubmitting(true);
    setIsStreaming(true);
    setStreamingReport("");
    setSelectedRecord(null);
    setError("");
    try {
      const createdRecord = await streamCreateReflection(
        {
          ...values,
          session_id: sessionId
        },
        {
          onDelta: (content) => {
            setStreamingReport((current) => current + content);
          }
        }
      );
      await loadRecords(sessionId);
      const detail = await getReflection(createdRecord.record_id, sessionId);
      setSelectedRecord(detail);
      setStreamingReport("");
      return true;
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "生成失败，请稍后重试。");
      return false;
    } finally {
      setIsSubmitting(false);
      setIsStreaming(false);
    }
  }

  async function handleSelectRecord(recordId: number) {
    if (!sessionId) {
      return;
    }

    setError("");
    try {
      const detail = await getReflection(recordId, sessionId);
      setSelectedRecord(detail);
    } catch {
      setError("详情加载失败，请稍后重试。");
    }
  }

  async function handleDeleteRecord(recordId: number) {
    if (!sessionId) {
      return;
    }

    setIsDeleting(true);
    setError("");
    try {
      await deleteReflection(recordId, sessionId);
      setSelectedRecord(null);
      await loadRecords(sessionId);
    } catch {
      setError("删除失败，请稍后重试。");
    } finally {
      setIsDeleting(false);
    }
  }

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,#dff3ea,transparent_34%),linear-gradient(135deg,#fffaf3,#edf7f2)] px-5 py-8 text-ink md:px-8">
      <section className="mx-auto flex max-w-7xl flex-col gap-8">
        <header className="rounded-[2rem] border border-white/70 bg-white/75 p-7 shadow-[0_24px_80px_rgba(23,32,51,0.12)] backdrop-blur md:p-9">
          <p className="mb-4 text-sm font-semibold uppercase tracking-[0.3em] text-clay">Stage 5 / Streaming Output</p>
          <div className="grid gap-6 lg:grid-cols-[1.4fr_0.6fr] lg:items-end">
            <div>
              <h1 className="text-4xl font-bold tracking-tight md:text-6xl">AI 情绪复盘助手</h1>
              <p className="mt-6 max-w-3xl text-lg leading-8 text-slate-700">
                当前阶段支持流式输出 AI 复盘报告：提交后可以实时看到内容生成，完成后自动保存到 SQLite 历史记录中。
              </p>
            </div>
            <div className="rounded-3xl bg-calm p-4 text-sm leading-6 text-slate-600">
              <p className="font-semibold text-ink">当前 session</p>
              <p className="mt-2 break-all font-mono text-xs">{sessionId || "初始化中..."}</p>
            </div>
          </div>
        </header>

        {error ? <div className="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div> : null}

        <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
          <ReflectionForm isSubmitting={isSubmitting} onSubmit={handleCreateReflection} />
          <div className="flex flex-col gap-6">
            <HistoryList records={records} selectedId={selectedRecord?.id} isLoading={isLoading} onSelect={handleSelectRecord} />
            <ReflectionDetail
              record={selectedRecord}
              streamingReport={streamingReport}
              isStreaming={isStreaming}
              isDeleting={isDeleting}
              onDelete={handleDeleteRecord}
            />
          </div>
        </div>

        <div className="rounded-3xl border border-amber-200 bg-amber-50 p-5 text-sm leading-7 text-amber-900">
          本工具仅用于心理学自助记录和情绪复盘，不提供诊断、治疗或医疗建议。
          如你正在经历严重痛苦、自伤想法或紧急危机，请立即联系身边可信任的人或当地专业机构。
        </div>
      </section>
    </main>
  );
}
