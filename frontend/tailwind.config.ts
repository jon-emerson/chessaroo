import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-display)', 'Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        glow: '0 25px 60px -35px rgba(45, 212, 191, 0.35)',
      },
      backgroundImage: {
        'hero-gradient':
          'linear-gradient(135deg, rgba(56,189,248,0.18) 0%, rgba(14,165,233,0.05) 45%, rgba(147,51,234,0.08) 100%)',
      },
    },
  },
  plugins: [],
};

export default config;
