"use client";

import { FormEvent, useState } from "react";

import type { FocusArea, ReflectionFormValues } from "../types/reflection";

const emotionOptions = ["焦虑", "愤怒", "委屈", "悲伤", "羞耻", "内疚", "失望", "压力", "其他"];
const focusOptions: FocusArea[] = ["情绪理解", "认知偏差", "人际关系", "行动建议", "综合分析"];

const initialValues: ReflectionFormValues = {
  event_text: "",
  emotion_tags: ["焦虑"],
  emotion_intensity: 5,
  automatic_thoughts: "",
  body_reaction: "",
  focus_area: "综合分析"
};

type ReflectionFormProps = {
  isSubmitting: boolean;
  onSubmit: (values: ReflectionFormValues) => Promise<boolean>;
};

export function ReflectionForm({ isSubmitting, onSubmit }: ReflectionFormProps) {
  const [values, setValues] = useState<ReflectionFormValues>(initialValues);

  function toggleEmotionTag(tag: string) {
    setValues((current) => {
      const hasTag = current.emotion_tags.includes(tag);
      const nextTags = hasTag ? current.emotion_tags.filter((item) => item !== tag) : [...current.emotion_tags, tag];
      return { ...current, emotion_tags: nextTags };
    });
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const isSuccess = await onSubmit(values);
    if (isSuccess) {
      setValues(initialValues);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="rounded-[2rem] border border-white/70 bg-white/80 p-6 shadow-sm">
      <div>
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-clay">Reflection Form</p>
        <h2 className="mt-2 text-2xl font-bold">开始一次情绪复盘</h2>
        <p className="mt-2 text-sm leading-6 text-slate-600">提交后由后端调用大模型，前端会实时展示生成中的复盘报告。</p>
      </div>

      <label className="mt-6 block">
        <span className="text-sm font-semibold">事件描述</span>
        <textarea
          required
          value={values.event_text}
          onChange={(event) => setValues({ ...values, event_text: event.target.value })}
          className="mt-2 min-h-28 w-full rounded-2xl border border-slate-200 bg-white p-4 outline-none transition focus:border-sage"
          placeholder="今天发生了什么？"
        />
      </label>

      <div className="mt-5">
        <span className="text-sm font-semibold">情绪标签</span>
        <div className="mt-3 flex flex-wrap gap-2">
          {emotionOptions.map((tag) => {
            const isSelected = values.emotion_tags.includes(tag);
            return (
              <button
                key={tag}
                type="button"
                onClick={() => toggleEmotionTag(tag)}
                className={`rounded-full border px-4 py-2 text-sm transition ${
                  isSelected ? "border-sage bg-sage text-white" : "border-slate-200 bg-white text-slate-700"
                }`}
              >
                {tag}
              </button>
            );
          })}
        </div>
      </div>

      <label className="mt-5 block">
        <span className="text-sm font-semibold">情绪强度：{values.emotion_intensity}</span>
        <input
          type="range"
          min="1"
          max="10"
          value={values.emotion_intensity}
          onChange={(event) => setValues({ ...values, emotion_intensity: Number(event.target.value) })}
          className="mt-3 w-full accent-sage"
        />
      </label>

      <label className="mt-5 block">
        <span className="text-sm font-semibold">自动想法</span>
        <input
          value={values.automatic_thoughts}
          onChange={(event) => setValues({ ...values, automatic_thoughts: event.target.value })}
          className="mt-2 w-full rounded-2xl border border-slate-200 bg-white p-3 outline-none transition focus:border-sage"
          placeholder="当时脑子里冒出了什么念头？"
        />
      </label>

      <label className="mt-5 block">
        <span className="text-sm font-semibold">身体反应</span>
        <input
          value={values.body_reaction}
          onChange={(event) => setValues({ ...values, body_reaction: event.target.value })}
          className="mt-2 w-full rounded-2xl border border-slate-200 bg-white p-3 outline-none transition focus:border-sage"
          placeholder="如胸闷、心跳加速、疲惫等"
        />
      </label>

      <label className="mt-5 block">
        <span className="text-sm font-semibold">重点分析方向</span>
        <select
          value={values.focus_area}
          onChange={(event) => setValues({ ...values, focus_area: event.target.value as FocusArea })}
          className="mt-2 w-full rounded-2xl border border-slate-200 bg-white p-3 outline-none transition focus:border-sage"
        >
          {focusOptions.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </label>

      <button
        type="submit"
        disabled={isSubmitting || values.emotion_tags.length === 0}
        className="mt-6 w-full rounded-2xl bg-ink px-5 py-3 font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-300"
      >
        {isSubmitting ? "流式生成中..." : "生成并保存复盘报告"}
      </button>
    </form>
  );
}
