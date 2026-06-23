/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        plum: {
          bg: '#F8F4EE',
          text: '#1F1F1F',
          muted: '#555555',
          primary: '#E5484D',
          hover: '#D43B40',
          purple: '#6F42C1',
          blue: '#4F8FF7',
          orange: '#F59E0B',
          pink: '#EC4899',
        }
      }
    },
  },
  plugins: [],
}