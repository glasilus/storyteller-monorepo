/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./components/**/*.{js,vue,ts}",
    "./layouts/**/*.vue",
    "./pages/**/*.vue",
    "./plugins/**/*.{js,ts}",
    "./nuxt.config.{js,ts}"
  ],
  theme: {
    extend: {
      colors: {
        
        'vg-bg': {
          DEFAULT: '#121224',        // основной фон
          softer: '#16162a',        // чуть светлее
          card: '#1a1a30',          // для карточек
        }
      }
    },
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: false, 
    base: true,
    styled: true,
    utils: true,
    rtl: false,
    prefix: "",
    logs: true,
  },
}