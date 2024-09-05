/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',  // Adjust the path according to your project structure
    './**/templates/**/*.html', // This covers templates in any subdirectory
    './static/js/*.js',   // Adjust if you have any JS files using Tailwind
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          '50': '#ecfeff',
          '100': '#cffafe',
          '200': '#a5f3fc',
          '300': '#67e8f9',
          '400': '#22d3ee',
          '500': '#06b6d4',
          '600': '#0891b2',
          '700': '#0e7490',
          '800': '#155e75',
          '900': '#164e63',
          '950': '#083344'
        }
      }
    },
    fontFamily: {
      'body': [
        'Inter',
        'ui-sans-serif',
        'system-ui',
        '-apple-system',
        'system-ui',
        'Segoe UI',
        'Roboto',
        'Helvetica Neue',
        'Arial',
        'Noto Sans',
        'sans-serif',
        'Apple Color Emoji',
        'Segoe UI Emoji',
        'Segoe UI Symbol',
        'Noto Color Emoji'
      ],
      'sans': [
        'Inter',
        'ui-sans-serif',
        'system-ui',
        '-apple-system',
        'system-ui',
        'Segoe UI',
        'Roboto',
        'Helvetica Neue',
        'Arial',
        'Noto Sans',
        'sans-serif',
        'Apple Color Emoji',
        'Segoe UI Emoji',
        'Segoe UI Symbol',
        'Noto Color Emoji'
      ]
    }
  },
  plugins: [],
}
