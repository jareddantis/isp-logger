/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./static/scripts/**/*.js",
    "./static/styles/**/*.css",
    "./templates/**/*.html"
  ],
  theme: {
    fontFamily: {
      sans: ['Roboto Flex', 'Inter', 'sans-serif']
    },
  },
  plugins: [],
}
