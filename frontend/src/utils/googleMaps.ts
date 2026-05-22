import { importLibrary, setOptions } from '@googlemaps/js-api-loader';

let mapsPromise: Promise<typeof google.maps> | null = null;
let placesPromise: Promise<typeof google.maps> | null = null;
let optionsSet = false;

export function getGoogleMapsApiKey(): string | null {
  const key = import.meta.env.VITE_GOOGLE_MAPS_API_KEY?.trim();
  return key || null;
}

function ensureOptions() {
  const apiKey = getGoogleMapsApiKey();
  if (!apiKey) {
    throw new Error(
      'Google Maps API key is missing. Add VITE_GOOGLE_MAPS_API_KEY to your .env file.',
    );
  }

  if (!optionsSet) {
    setOptions({
      key: apiKey,
      v: 'weekly',
      language: 'en',
    });
    optionsSet = true;
  }
}

export function loadGoogleMaps(): Promise<typeof google.maps> {
  if (mapsPromise) {
    return mapsPromise;
  }

  ensureOptions();
  mapsPromise = Promise.all([importLibrary('maps'), importLibrary('streetView')]).then(
    () => google.maps,
  );
  return mapsPromise;
}

export function loadGooglePlaces(): Promise<typeof google.maps> {
  if (placesPromise) {
    return placesPromise;
  }

  ensureOptions();
  placesPromise = Promise.all([
    importLibrary('maps'),
    importLibrary('places'),
    importLibrary('geocoding'),
  ]).then(() => google.maps);
  return placesPromise;
}

export function getGoogleMapsLoadHint(error: unknown): string {
  if (error instanceof Error && error.message.includes('missing')) {
    return error.message;
  }

  return 'Google Maps could not load. Enable Maps JavaScript API, Places API, and Geocoding API for your key, and allow http://localhost:5173 in key restrictions.';
}
