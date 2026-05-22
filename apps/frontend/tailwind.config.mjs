/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './src/**/*.{astro,html,js,jsx,ts,tsx,md,mdx}',
    'node_modules/flowbite-react/**/*.{js,jsx,ts,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        surface: '#ffffff',
        ink: '#101828',
        lime: {
          50: '#f7fee7',
          100: '#ecfccb',
          500: '#84cc16',
          600: '#65a30d'
        }
      },
      boxShadow: {
        soft: '0 10px 30px rgba(16,24,40,0.08)'
      }
    }
  },
  plugins: [
    require('flowbite/plugin')
  ]
};
