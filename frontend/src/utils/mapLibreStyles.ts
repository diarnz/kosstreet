export type MapLibreStyleKey = 'carto' | 'openstreetmap' | 'openstreetmap3d';

export const MAPLIBRE_CARTO_STYLES = {
  light: 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
  dark: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
};

export const MAPLIBRE_STYLE_URLS: Record<MapLibreStyleKey, string> = {
  carto: MAPLIBRE_CARTO_STYLES.light,
  openstreetmap: 'https://tiles.openfreemap.org/styles/bright',
  openstreetmap3d: 'https://tiles.openfreemap.org/styles/liberty',
};

export const MAPLIBRE_STYLE_LABELS: Record<MapLibreStyleKey, string> = {
  carto: 'Carto',
  openstreetmap: 'OpenStreetMap',
  openstreetmap3d: 'OpenStreetMap 3D',
};

export function isMapLibre3dStyle(styleKey: MapLibreStyleKey): boolean {
  return styleKey === 'openstreetmap3d';
}

export function mapStyleSupportsDarkMode(styleKey: MapLibreStyleKey): boolean {
  return styleKey === 'carto' || styleKey === 'openstreetmap';
}

export function resolveMapStyleUrl(styleKey: MapLibreStyleKey, isDark: boolean): string {
  if (isMapLibre3dStyle(styleKey)) {
    return MAPLIBRE_STYLE_URLS.openstreetmap3d;
  }

  if (isDark && mapStyleSupportsDarkMode(styleKey)) {
    return MAPLIBRE_CARTO_STYLES.dark;
  }

  return MAPLIBRE_STYLE_URLS[styleKey];
}
