/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './src/pages/**/*.{ts,tsx}',
    './src/components/**/*.{ts,tsx}',
    './src/app/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#070b12',
        surface: '#0d1522',
        'surface-elevated': '#131e2e',
        border: '#1e2e44',
        // User requested palette: #E3FDFD, #CBF1F5, #A6E3E9, #71C9CE
        brand: {
          ice: '#E3FDFD',
          soft: '#CBF1F5',
          cyan: '#A6E3E9',
          teal: '#71C9CE',
        },
        // Non-neon, executive pentesting severity tones
        pentest: {
          critical: '#dc2626',
          high: '#ea580c',
          medium: '#d97706',
          low: '#71c9ce',
          clean: '#10b981',
        },
        slate: {
          950: '#070b12',
          900: '#0d1522',
          850: '#131e2e',
          800: '#1a293e',
          750: '#243852',
          700: '#324b6d',
        },
      },
      fontFamily: {
        jakarta: ["'Plus Jakarta Sans'", 'Inter', 'sans-serif'],
        sans: ["'Plus Jakarta Sans'", 'Inter', 'system-ui', 'sans-serif'],
        mono: ["'JetBrains Mono'", 'monospace'],
      },
    },
  },
  plugins: [],
}
