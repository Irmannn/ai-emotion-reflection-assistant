"use client";

import type { ReflectionListItem } from "../types/reflection";

type HistoryListProps = {
  records: ReflectionListItem[];
  selectedId?: number;
  isLoading: boolean;
  onSelect: (recordId: number) => void;
};

function formatCreatedAt(createdAt: string) {
  const hasTimezone = /(?:Z|[+-]\d{2}:\d{2})$/.test(createdAt);
  const date = new Date(hasTimezone ? createdAt : `${createdAt}Z`);

  return date.toLocaleString("zh-CN", {
    timeZone: "Asia/Shanghai",
    hour12: false
  });
}

export function HistoryList({ records, selectedId, isLoading, onSelect }: HistoryListProps) {
  return (
    <section className="rounded-[2rem] border border-white/70 bg-white/75 p-6 shadow-sm">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-clay">History</p>
          <h2 className="mt-2 text-2xl font-bold">历史记录</h2>
        </div>
        <span className="rounded-full bg-calm px-3 py-1 text-sm text-slate-600">{records.length} 条</span>
      </div>

      <div className="mt-5 space-y-3">
        {isLoading ? <p className="text-sm text-slate-500">正在加载历史记录...</p> : null}

        {!isLoading && records.length === 0 ? (
          <p className="rounded-2xl border border-dashed border-slate-200 p-4 text-sm leading-6 text-slate-500">
            还没有历史记录。提交一次表单后，这里会展示当前 session 的复盘记录。
          </p>
        ) : null}

        {records.map((record) => (
          <button
            key={record.id}
            type="button"
            onClick={() => onSelect(record.id)}
            className={`w-full rounded-2xl border p-4 text-left transition ${
              selectedId === record.id ? "border-sage bg-calm" : "border-slate-100 bg-white hover:border-sage/60"
            }`}
          >
            <div className="flex items-center justify-between gap-3">
              <span className="font-semibold">{record.event_summary}</span>
              <span className="rounded-full bg-white px-2 py-1 text-xs text-slate-500">强度 {record.emotion_intensity}</span>
            </div>
            <p className="mt-2 text-sm text-slate-600">{record.emotion_tags}</p>
            <p className="mt-2 text-xs text-slate-400">{formatCreatedAt(record.created_at)}</p>
          </button>
        ))}
      </div>
    </section>
  );
}
