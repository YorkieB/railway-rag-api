/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
    "./app/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        neon: {
          blue: "#4fc3f7",
          violet: "#8b5cf6",
          cyan: "#5ef1ff"
        },
        glass: "rgba(255,255,255,0.08)"
      },
      boxShadow: {
        glow: "0 0 25px rgba(79,195,247,0.45)",
        "glow-strong": "0 0 45px rgba(139,92,246,0.55)"
      },
      backdropBlur: {
        xs: "2px"
      }
    }
  },
  plugins: []
};

