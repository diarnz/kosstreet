import type { IssueCategory } from '@/types/report';

export interface CategoryMarkerStyle {
  fill: string;
  stroke: string;
  glyph: string;
}

export const categoryMarkerStyles: Record<IssueCategory, CategoryMarkerStyle> = {
  pothole: {
    fill: '#3a3f3b',
    stroke: '#252826',
    glyph: `<path d="M9 14c1.2-2.4 2.4-2.4 3.6-1.2s2.4 1.2 3.6-1.2 2.4-1.2 2.4 1.2" stroke="#3a3f3b" stroke-width="1.6" stroke-linecap="round" fill="none"/>
      <circle cx="11" cy="15.2" r="1.1" fill="#3a3f3b"/>
      <circle cx="17" cy="13.8" r="1.1" fill="#3a3f3b"/>`,
  },
  garbage: {
    fill: '#3d6b55',
    stroke: '#2a4a3b',
    glyph: `<path d="M11.5 9.5h5M12 9.5V8h4v1.5M10.5 11.5h7l-.8 8.5h-5.4l-.8-8.5z" stroke="#3d6b55" stroke-width="1.4" stroke-linejoin="round" fill="none"/>`,
  },
  broken_streetlight: {
    fill: '#d9902f',
    stroke: '#a66a1f',
    glyph: `<path d="M14 7.5v2.2M11.5 18.5h5M12.5 9.7h3v5.8a1.5 1.5 0 01-3 0V9.7z" stroke="#d9902f" stroke-width="1.4" stroke-linecap="round" fill="none"/>
      <path d="M10.5 13.5h7" stroke="#d9902f" stroke-width="1.4" stroke-linecap="round"/>`,
  },
  blocked_sidewalk: {
    fill: '#5a7d8c',
    stroke: '#3f5c68',
    glyph: `<path d="M8 16.5h12M9.5 16.5V9.5l3-2.2 3 2.2v7M15.5 16.5v-4.8l3.2 2.2v2.6" stroke="#5a7d8c" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" fill="none"/>`,
  },
  damaged_sign: {
    fill: '#bf6841',
    stroke: '#8f4d2f',
    glyph: `<path d="M14 8.2l4.8 2.8-4.8 2.8-4.8-2.8 4.8-2.8z" stroke="#bf6841" stroke-width="1.4" stroke-linejoin="round" fill="none"/>
      <path d="M14 13.8v4.2M11.8 18h4.4" stroke="#bf6841" stroke-width="1.4" stroke-linecap="round"/>`,
  },
  other: {
    fill: '#6b6560',
    stroke: '#4f4b47',
    glyph: `<circle cx="14" cy="13.5" r="4.2" stroke="#6b6560" stroke-width="1.4" fill="none"/>
      <path d="M14 11.2v3.2M14 15.8h.01" stroke="#6b6560" stroke-width="1.6" stroke-linecap="round"/>`,
  },
};

const iconCache = new Map<string, google.maps.Icon>();
const svgUrlCache = new Map<string, string>();

function buildMarkerSvg(category: IssueCategory, selected: boolean): string {
  const style = categoryMarkerStyles[category];
  const width = selected ? 44 : 36;
  const height = selected ? 52 : 44;
  const ring = selected
    ? `<circle cx="18" cy="17" r="15.5" fill="none" stroke="#ffffff" stroke-width="3"/>`
    : '';

  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 36 44">
    ${ring}
    <path d="M18 1.5C10.5 1.5 4.5 7.5 4.5 15c0 11.2 13.5 27.5 13.5 27.5S31.5 26.2 31.5 15C31.5 7.5 25.5 1.5 18 1.5z" fill="${style.fill}" stroke="${style.stroke}" stroke-width="1.2"/>
    <circle cx="18" cy="15" r="8.5" fill="#ffffff"/>
    <g transform="translate(4 4)">${style.glyph}</g>
  </svg>`;
}

export function getCategoryMarkerSvgUrl(category: IssueCategory, selected = false): string {
  const cacheKey = `${category}:${selected ? '1' : '0'}`;
  const cached = svgUrlCache.get(cacheKey);
  if (cached) {
    return cached;
  }

  const url = `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(buildMarkerSvg(category, selected))}`;
  svgUrlCache.set(cacheKey, url);
  return url;
}

export function getCategoryMarkerIcon(
  category: IssueCategory,
  selected = false,
): google.maps.Icon {
  const cacheKey = `${category}:${selected ? '1' : '0'}`;
  const cached = iconCache.get(cacheKey);
  if (cached) {
    return cached;
  }

  const width = selected ? 44 : 36;
  const height = selected ? 52 : 44;
  const icon: google.maps.Icon = {
    url: getCategoryMarkerSvgUrl(category, selected),
    scaledSize: new google.maps.Size(width, height),
    anchor: new google.maps.Point(width / 2, height - 2),
  };
  iconCache.set(cacheKey, icon);
  return icon;
}
