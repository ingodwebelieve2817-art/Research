/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./**/templates/**/*.html",
    "./static/**/*.js",
    "./frontend_pricing/src/**/*.{ts,tsx,js,jsx}"
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        heading: ['Outfit', 'sans-serif'],
      },
      colors: {
        brand: {
          dark: '#030712',
          card: '#0b0f19',
          accent: '#6366f1',
          accentHover: '#4f46e5',
        }
      },
      boxShadow: {
        'glow': '0 0 25px -5px rgba(99, 102, 241, 0.2)',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
