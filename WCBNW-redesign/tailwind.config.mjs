/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        /* ── Deep layers (forest floor) ── */
        forest: { DEFAULT: '#0f2318', light: '#1a3a2a' },
        canopy: '#162e20',
        fern: { DEFAULT: '#2d5a3f', light: '#4a7a5e' },
        sage: '#7a9e7e',

        /* ── Warm layers (earth & wood) ── */
        cedar: { DEFAULT: '#6b3a1f', light: '#8b5e3c' },
        bark: '#4a3628',
        driftwood: { DEFAULT: '#bfb5a3', light: '#d4cfc5' },

        /* ── Atmospheric layers (fog & sky) ── */
        mist: { DEFAULT: '#e8e4df', dark: '#d8d2ca' },
        cloud: '#f7f5f1',

        /* ── Water layers ── */
        tide: { DEFAULT: '#3a5a6e', dark: '#2a4858', light: '#5a7a8e' },
        storm: '#1e2d3d',

        /* ── Accent layers (fire & light) ── */
        ember: { DEFAULT: '#c46a35', dark: '#a85a2d', light: '#d4884f' },
        gold: '#d4a745',

        /* ── Neutrals ── */
        stone: '#8c8677',
      },
      fontFamily: {
        display: ['"Cormorant Garamond"', 'Georgia', 'serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
      },
      letterSpacing: {
        'wide-caps': '0.15em',
        'wider-caps': '0.25em',
      },
      animation: {
        'fog-1': 'fogDrift1 35s linear infinite',
        'fog-2': 'fogDrift2 25s linear infinite',
        'fog-3': 'fogDrift3 45s linear infinite',
        'slow-zoom': 'slowZoom 30s ease-in-out infinite alternate',
        'fade-up': 'fadeUp 0.8s ease-out forwards',
        'fade-in': 'fadeIn 1s ease-out forwards',
        'slide-down': 'slideDown 0.3s ease-out forwards',
        'breathe': 'breathe 8s ease-in-out infinite',
        'drift-in': 'driftIn 1.2s ease-out forwards',
      },
      keyframes: {
        fogDrift1: {
          '0%': { transform: 'translateX(-33.33%)' },
          '100%': { transform: 'translateX(0%)' },
        },
        fogDrift2: {
          '0%': { transform: 'translateX(0%)' },
          '100%': { transform: 'translateX(-33.33%)' },
        },
        fogDrift3: {
          '0%': { transform: 'translateX(-16.66%)' },
          '100%': { transform: 'translateX(-50%)' },
        },
        slowZoom: {
          '0%': { transform: 'scale(1)' },
          '100%': { transform: 'scale(1.08)' },
        },
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(30px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideDown: {
          '0%': { opacity: '0', transform: 'translateY(-10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        breathe: {
          '0%, 100%': { opacity: '0.3' },
          '50%': { opacity: '0.6' },
        },
        driftIn: {
          '0%': { opacity: '0', transform: 'translateY(40px) scale(0.97)' },
          '100%': { opacity: '1', transform: 'translateY(0) scale(1)' },
        },
      },
    },
  },
  plugins: [],
};
