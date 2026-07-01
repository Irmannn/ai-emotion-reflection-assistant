import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI 情绪复盘助手",
  description: "一个用于练习 AI 全栈闭环的情绪复盘 MVP"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
