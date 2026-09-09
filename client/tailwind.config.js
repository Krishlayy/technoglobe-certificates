/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#F0F5FA',
          100: '#E1EBF5',
          200: '#BAD0E8',
          300: '#8FB4DA',
          400: '#5F93C9',
          500: '#134074',
          600: '#0E325D',
          700: '#0B2545',
          800: '#081C34',
          900: '#051222',
        },
        gold: {
          50: '#FAF8F0',
          100: '#F3EEDB',
          200: '#E5D7A9',
          300: '#D7BF77',
          400: '#C9A845',
          500: '#B89223',
          600: '#9E7A18',
          700: '#7E6012',
          800: '#5E470D',
        }
      },
      fontFamily: {
        serif: ['"Cinzel"', '"Playfair Display"', 'Georgia', 'serif'],
        sans: ['"Inter"', 'system-ui', '-apple-system', 'sans-serif'],
      },
      screens: {
        'print': {'raw': 'print'},
      }
    },
  },
  plugins: [],
}
