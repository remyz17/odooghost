/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        primary: '#714B67'
      }
    }
  },
  plugins: [require('@tailwindcss/forms')]
}
