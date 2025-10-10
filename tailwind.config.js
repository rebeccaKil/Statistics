/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  safelist: [
    // 동적 색상 클래스 보존 (Tailwind 색상 팔레트 주요군)
    { pattern: /(bg|text)-(rose|pink|fuchsia|purple|violet|indigo|blue|sky|cyan|teal|emerald|green|lime|yellow|amber|orange|red)-(100|400|500|600)/ },
  ],
  theme: {
    extend: {
      animation: {
        'grow': 'grow 1.5s ease-out forwards',
      },
      keyframes: {
        grow: {
          'from': { transform: 'scaleX(0)' },
          'to': { transform: 'scaleX(1)' },
        },
      },
    },
  },
  plugins: [],
}
