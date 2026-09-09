/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['class'],
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: 'rgb(var(--color-primary) / <alpha-value>)',
          light: 'rgb(var(--color-primary-light) / <alpha-value>)',
          dark: 'rgb(var(--color-primary-dark) / <alpha-value>)',
        },
        secondary: {
          DEFAULT: 'rgb(var(--color-secondary) / <alpha-value>)',
        },
        accent: {
          DEFAULT: 'rgb(var(--color-accent) / <alpha-value>)',
        },
        background: 'rgb(var(--color-background) / <alpha-value>)',
        surface: 'rgb(var(--color-surface) / <alpha-value>)',
        ink: {
          DEFAULT: 'rgb(var(--color-ink) / <alpha-value>)',
          soft: 'rgb(var(--color-ink-soft) / <alpha-value>)',
        },
        gold: {
          DEFAULT: 'rgb(var(--color-gold) / <alpha-value>)',
          light: 'rgb(var(--color-gold-light) / <alpha-value>)',
        },
      },
      fontFamily: {
        // Apple system stack for the application UI - never a bundled Apple font file.
        sans: [
          '-apple-system', 'BlinkMacSystemFont', '"SF Pro Display"', '"SF Pro Text"',
          '"Helvetica Neue"', 'Arial', 'ui-sans-serif', 'system-ui', 'sans-serif',
        ],
        // Optional reader-only serif for Scripture reading preference (not used app-wide).
        display: ['"Fraunces"', 'ui-serif', 'Georgia', 'serif'],
      },
      borderRadius: {
        sm: '0.625rem',   // 10px
        DEFAULT: '0.625rem',
        md: '0.875rem',   // 14px
        lg: '1.125rem',   // 18px
        xl: '1.5rem',     // 24px
        '2xl': '1.5rem',  // 24px (kept for existing usage)
        '3xl': '1.875rem', // 30px
      },
      boxShadow: {
        soft: '0 2px 8px rgba(11, 93, 59, 0.06), 0 8px 24px rgba(11, 93, 59, 0.06)',
        card: '0 1px 2px rgba(27,27,27,0.04), 0 8px 30px rgba(11,93,59,0.08)',
        glow: '0 0 0 4px rgba(121, 193, 65, 0.18)',
      },
      keyframes: {
        'grow-in': {
          '0%': { transform: 'scale(0.9) translateY(6px)', opacity: '0' },
          '100%': { transform: 'scale(1) translateY(0)', opacity: '1' },
        },
        'flame-flicker': {
          '0%, 100%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.06)' },
        },
      },
      animation: {
        'grow-in': 'grow-in 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
        'flame-flicker': 'flame-flicker 2s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
