"use client";

import type { ReflectionDetail as ReflectionDetailType } from "../types/reflection";

type ReflectionDetailProps = {
  record: ReflectionDetailType | null;
  streamingReport: string;
  isStreaming: boolean;
  isDeleting: boolean;
  onDelete: (recordId: number) => Promise<void>;
};

export function ReflectionDetail({ record, streamingReport, isStreaming, isDeleting, onDelete }: ReflectionDetailProps) {
  if (isStreaming || streamingReport) {
    return (
      <section className="rounded-[2rem] border border-teal-100 bg-white/80 p-6 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-clay">Streaming</p>
        <h2 className="mt-2 text-2xl font-bold">AI 复盘报告生成中</h2>
        <div className="mt-5 rounded-2xl bg-white p-4 text-sm text-slate-700">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
            {isStreaming ? "实时输出" : "生成结果"}
          </p>
          <p className="mt-2 min-h-32 whitespace-pre-wrap leading-7">
            {streamingReport || "正在连接模型服务，请稍等..."}
          </p>
        </div>
      </section>
    );
  }

  if (!record) {
    return (
      <section className="rounded-[2rem] border border-white/70 bg-white/65 p-6 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-clay">Detail</p>
        <h2 className="mt-2 text-2xl font-bold">复盘详情</h2>
        <p className="mt-4 rounded-2xl border border-dashed border-slate-200 p-4 text-sm leading-6 text-slate-500">
          从历史记录中选择一条，查看完整输入和 AI 复盘报告。
        </p>
      </section>
    );
  }

  return (
    <section className="rounded-[2rem] border border-white/70 bg-white/80 p-6 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-clay">Detail</p>
          <h2 className="mt-2 text-2xl font-bold">复盘详情</h2>
        </div>
        <button
          type="button"
          onClick={() => onDelete(record.id)}
          disabled={isDeleting}
          className="rounded-full border border-red-200 px-4 py-2 text-sm font-semibold text-red-600 transition hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isDeleting ? "删除中..." : "删除"}
        </button>
      </div>

      <div className="mt-5 grid gap-4 text-sm text-slate-700">
        <DetailItem label="事件描述" value={record.event_text} />
        <DetailItem label="情绪标签" value={record.emotion_tags} />
        <DetailItem label="情绪强度" value={String(record.emotion_intensity)} />
        <DetailItem label="自动想法" value={record.automatic_thoughts || "未填写"} />
        <DetailItem label="身体反应" value={record.body_reaction || "未填写"} />
        <DetailItem label="分析方向" value={record.focus_area} />
        <DetailItem label="AI 复盘报告" value={record.ai_report || "暂无"} />
        <ReferenceList references={record.references} />
      </div>
    </section>
  );
}

function DetailItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl bg-white p-4">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">{label}</p>
      <p className="mt-2 whitespace-pre-wrap leading-7">{value}</p>
    </div>
  );
}

function ReferenceList({ references }: { references: ReflectionDetailType["references"] }) {
  const safeReferences = references ?? [];

  if (!safeReferences.length) {
    return <DetailItem label="参考资料" value="本次未检索到知识库参考资料。" />;
  }

  return (
    <div className="rounded-2xl bg-white p-4">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">参考资料</p>
      <div className="mt-3 grid gap-3">
        {safeReferences.map((reference, index) => (
          <div key={`${reference.source}-${reference.title}-${index}`} className="rounded-xl border border-slate-100 bg-slate-50 p-3">
            <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500">
              <span className="rounded-full bg-white px-2 py-1 font-semibold text-sage">Top {index + 1}</span>
              <span>相关度 {reference.score.toFixed(4)}</span>
            </div>
            <p className="mt-2 font-semibold text-ink">{reference.title}</p>
            <p className="mt-1 text-xs text-slate-500">{reference.source}</p>
            <p className="mt-2 whitespace-pre-wrap leading-6 text-slate-700">{reference.content_preview}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
