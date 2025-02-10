/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './eatwellapp/templates/**/*.html',
    "./**/*.js", "./**/*.py", "./**/*.jsx", "./**/*.tsx",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Poppins', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

