type Shades = { bg100: string; text600: string; bar400: string; text500: string };

const palette: Record<string, Shades> = {
  indigo: { bg100: '#e0e7ff', text600: '#4f46e5', bar400: '#818cf8', text500: '#6366f1' },
  orange: { bg100: '#ffedd5', text600: '#ea580c', bar400: '#fb923c', text500: '#f97316' },
  sky: { bg100: '#e0f2fe', text600: '#0284c7', bar400: '#38bdf8', text500: '#0ea5e9' },
  red: { bg100: '#fee2e2', text600: '#dc2626', bar400: '#f87171', text500: '#ef4444' },
  blue: { bg100: '#dbeafe', text600: '#2563eb', bar400: '#60a5fa', text500: '#3b82f6' },
  green: { bg100: '#dcfce7', text600: '#16a34a', bar400: '#4ade80', text500: '#22c55e' },
  purple: { bg100: '#f3e8ff', text600: '#9333ea', bar400: '#c084fc', text500: '#a855f7' },
  pink: { bg100: '#fce7f3', text600: '#db2777', bar400: '#f472b6', text500: '#ec4899' },
  yellow: { bg100: '#fef3c7', text600: '#d97706', bar400: '#fbbf24', text500: '#f59e0b' },
  teal: { bg100: '#ccfbf1', text600: '#0f766e', bar400: '#2dd4bf', text500: '#14b8a6' },
  cyan: { bg100: '#cffafe', text600: '#0e7490', bar400: '#22d3ee', text500: '#06b6d4' },
  rose: { bg100: '#ffe4e6', text600: '#e11d48', bar400: '#fb7185', text500: '#f43f5e' },
  emerald: { bg100: '#d1fae5', text600: '#059669', bar400: '#34d399', text500: '#10b981' },
  violet: { bg100: '#ede9fe', text600: '#7c3aed', bar400: '#a78bfa', text500: '#8b5cf6' },
  fuchsia: { bg100: '#fae8ff', text600: '#c026d3', bar400: '#e879f9', text500: '#d946ef' },
};

export function getShades(color: string): Shades {
  return palette[color] || palette.indigo;
}

export const colorOptions = [
  { value: 'indigo', label: 'Indigo', preview: '#6366f1' },
  { value: 'orange', label: 'Orange', preview: '#f97316' },
  { value: 'sky', label: 'Sky', preview: '#0ea5e9' },
  { value: 'red', label: 'Red', preview: '#ef4444' },
  { value: 'blue', label: 'Blue', preview: '#3b82f6' },
  { value: 'green', label: 'Green', preview: '#22c55e' },
  { value: 'purple', label: 'Purple', preview: '#a855f7' },
  { value: 'pink', label: 'Pink', preview: '#ec4899' },
  { value: 'yellow', label: 'Yellow', preview: '#f59e0b' },
  { value: 'teal', label: 'Teal', preview: '#14b8a6' },
  { value: 'cyan', label: 'Cyan', preview: '#06b6d4' },
  { value: 'rose', label: 'Rose', preview: '#f43f5e' },
  { value: 'emerald', label: 'Emerald', preview: '#10b981' },
  { value: 'violet', label: 'Violet', preview: '#8b5cf6' },
  { value: 'fuchsia', label: 'Fuchsia', preview: '#d946ef' },
];


