import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#172033",
        calm: "#eef8f4",
        sage: "#7da391",
        clay: "#c97854"
      }
    }
  },
  plugins: []
};

export default config;
