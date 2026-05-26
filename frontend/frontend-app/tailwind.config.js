/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        industrial: {
          950: "#071011",
          900: "#0b1718",
          850: "#0f1f20",
          800: "#132829",
          700: "#1c393a"
        },
        signal: {
          green: "#54e1a6",
          amber: "#f5b84b",
          red: "#ff6b6b",
          cyan: "#5bd8ff"
        }
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(91,216,255,.08), 0 18px 50px rgba(0,0,0,.28)"
      }
    }
  },
  plugins: []
};
