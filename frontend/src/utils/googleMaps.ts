import { importLibrary, setOptions } from '@googlemaps/js-api-loader';

let mapsPromise: Promise<typeof google.maps> | null = null;
let optionsSet = false;

export function getGoogleMapsApiKey(): string | null {
  const key = import.meta.env.VITE_GOOGLE_MAPS_API_KEY?.trim();
  return key || null;
}

export function loadGoogleMaps(): Promise<typeof google.maps> {
  if (mapsPromise) {
    return mapsPromise;
  }

  const apiKey = getGoogleMapsApiKey();
  if (!apiKey) {
    return Promise.reject(
      new Error('Google Maps browser API key is missing. Set VITE_GOOGLE_MAPS_API_KEY.'),
    );
  }

  if (!optionsSet) {
    setOptions({
      key: apiKey,
      v: 'weekly',
    });
    optionsSet = true;
  }

  mapsPromise = importLibrary('streetView').then(() => google.maps);
  return mapsPromise;
}
