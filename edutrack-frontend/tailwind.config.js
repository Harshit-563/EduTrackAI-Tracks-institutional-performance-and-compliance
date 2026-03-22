/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 60-30-10 Color Palette
        // 60% - Base/Dominant Colors
        slate: {
          50: "#f8fafc",
          100: "#f1f5f9",
          200: "#e2e8f0",
          300: "#cbd5e1",
          400: "#94a3b8",
          500: "#64748b",
          600: "#475569",
          700: "#334155",
          800: "#1e293b",
          900: "#0f172a",
        },
        // 30% - Primary Accent Colors
        primary: "#5b6ee1",      // Soft blue-purple
        primary_light: "#7c8ff5",
        primary_dark: "#4c5fd1",
        secondary: "#6d28d9",     // Deep purple
        secondary_light: "#8b5cf6",
        secondary_dark: "#5b21b6",
        // 10% - Accent/Highlight Colors
        accent: "#ec4899",        // Vibrant pink
        success: "#10b981",       // Green
        warning: "#f59e0b",       // Amber
        danger: "#ef4444",        // Red
        info: "#06b6d4",          // Cyan
      },
      backgroundImage: {
        "gradient-primary": "linear-gradient(135deg, #5b6ee1 0%, #6d28d9 100%)",
        "gradient-accent": "linear-gradient(135deg, #ec4899 0%, #f59e0b 100%)",
      },
    },
  },
  plugins: [],
}
