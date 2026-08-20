/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [
    "./templates/**/*.html",
    "./**/templates/**/*.html",
    "./**/*.html",
    "./static/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          primary: "#1A1A1A",
          primaryDark: "#0D0D0D",
          primaryLight: "#333333",
          secondary: "#D3AA5E",
          accent: "#C48E37",
          accentDark: "#99601D",
          light: "#F8F9FA",
          soft: "#F1F3F5",
          card: "#FFFFFF",
          sand: "#FAF5E9",
          dark: "#141414",
          gray: "#6C757D",
          lightText: "#ADB5BD",
          success: "#28A745",
          warning: "#FFC107",
          danger: "#DC3545",
          gold: "#D3AA5E",
          goldDark: "#B47825",
          goldLight: "#F3E7CA",
          darkCard: "#1E1E1E",
          darkBorder: "#2D2D2D",
        },
        luxuryGold: {
          50: '#FAF5E9',
          100: '#F3E7CA',
          200: '#E5CC94',
          300: '#D3AA5E',
          400: '#C48E37',
          500: '#B47825',
          600: '#99601D',
          700: '#784817',
          800: '#5D3713',
          900: '#4D2E11',
        }
      },
      backgroundImage: {
        hero: "linear-gradient(to right, rgba(0,0,0,0.85), rgba(0,0,0,0.35))",
        heroGradient: "linear-gradient(to right, rgba(0,0,0,0.85), rgba(0,0,0,0.35))",
        goldGradient: "linear-gradient(135deg, #D3AA5E 0%, #B47825 100%)",
      },
      boxShadow: {
        soft: "0 8px 25px rgba(0,0,0,0.08)",
        hover: "0 20px 45px rgba(211,170,94,0.18)",
        glow: "0 0 30px rgba(211,170,94,0.25)",
        luxury: "0 20px 45px rgba(0,0,0,0.20)",
        card: "0 8px 25px rgba(0,0,0,0.08)"
      },
      borderRadius: {
        xl: "16px",
        "2xl": "22px",
        "3xl": "30px"
      },
      fontFamily: {
        heading: ['"Playfair Display"', "serif"],
        playfair: ['"Playfair Display"', "serif"],
        serif: ['"Playfair Display"', "serif"],
        sans: ["Outfit", "sans-serif"],
        body: ["Outfit", "sans-serif"],
      }
    },
  },
  plugins: [],
}
