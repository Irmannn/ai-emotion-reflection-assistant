const stageItems = [
  "Next.js 前端骨架",
  "FastAPI 后端骨架",
  "后端 /health 健康检查",
  "README 本地启动说明"
];

export default function Home() {
  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,#dff3ea,transparent_34%),linear-gradient(135deg,#fffaf3,#edf7f2)] px-6 py-10 text-ink">
      <section className="mx-auto flex max-w-5xl flex-col gap-10">
        <div className="rounded-[2rem] border border-white/70 bg-white/75 p-8 shadow-[0_24px_80px_rgba(23,32,51,0.12)] backdrop-blur">
          <p className="mb-4 text-sm font-semibold uppercase tracking-[0.3em] text-clay">
            Stage 1 / Project Skeleton
          </p>
          <h1 className="text-4xl font-bold tracking-tight md:text-6xl">AI 情绪复盘助手</h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-700">
            当前阶段先完成一个最小可运行的前后端分离骨架。后续会逐步接入
            SQLite、LLM API、流式输出和历史记录。
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          {stageItems.map((item, index) => (
            <div key={item} className="rounded-3xl border border-white/70 bg-white/70 p-5 shadow-sm">
              <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-sage text-sm font-bold text-white">
                {index + 1}
              </span>
              <p className="mt-4 font-semibold">{item}</p>
            </div>
          ))}
        </div>

        <div className="rounded-3xl border border-amber-200 bg-amber-50 p-5 text-sm leading-7 text-amber-900">
          本工具仅用于心理学自助记录和情绪复盘，不提供诊断、治疗或医疗建议。
          如你正在经历严重痛苦、自伤想法或紧急危机，请立即联系身边可信任的人或当地专业机构。
        </div>
      </section>
    </main>
  );
}
