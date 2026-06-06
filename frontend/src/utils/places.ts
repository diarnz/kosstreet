import { KOSOVO_BOUNDS, KOSOVO_DEFAULT_VIEWPORT } from '@/utils/map';
import { loadGooglePlaces } from '@/utils/googleMaps';

export interface PlaceSelection {
  latitude: number;
  longitude: number;
  label: string;
}

export function getKosovoPlaceAutocompleteOptions(): google.maps.places.PlaceAutocompleteElementOptions {
  return {
    includedRegionCodes: ['XK'],
    locationBias: {
      center: {
        lat: KOSOVO_DEFAULT_VIEWPORT.center.latitude,
        lng: KOSOVO_DEFAULT_VIEWPORT.center.longitude,
      },
      radius: 65000,
    },
    requestedRegion: 'XK',
    noInputIcon: true,
  };
}

/** @deprecated Legacy autocomplete — prefer PlaceAutocompleteElement options above. */
export function getKosovoAutocompleteOptions(): google.maps.places.AutocompleteOptions {
  return {
    bounds: KOSOVO_BOUNDS,
    strictBounds: false,
    componentRestrictions: { country: 'xk' },
    fields: ['geometry', 'formatted_address', 'name'],
  };
}

export function getPlacesMapOptions(): google.maps.MapOptions {
  return {
    center: {
      lat: KOSOVO_DEFAULT_VIEWPORT.center.latitude,
      lng: KOSOVO_DEFAULT_VIEWPORT.center.longitude,
    },
    zoom: 9,
    restriction: {
      latLngBounds: KOSOVO_BOUNDS,
      strictBounds: false,
    },
    // Hide default Google Maps UI so the map canvas is clean — keep map tiles and attribution
    disableDefaultUI: true,
    zoomControl: false,
    mapTypeControl: false,
    streetViewControl: false,
    fullscreenControl: false,
    keyboardShortcuts: false,
  };
}

export function placeToSelection(place: google.maps.places.PlaceResult): PlaceSelection | null {
  const location = place.geometry?.location;
  if (!location) {
    return null;
  }

  const label = place.formatted_address?.trim() || place.name?.trim() || 'Selected location';

  return {
    latitude: Number(location.lat().toFixed(6)),
    longitude: Number(location.lng().toFixed(6)),
    label,
  };
}

export async function placeDetailsToSelection(
  place: google.maps.places.Place,
): Promise<PlaceSelection | null> {
  await place.fetchFields({ fields: ['location', 'formattedAddress', 'displayName'] });
  const location = place.location;
  if (!location) {
    return null;
  }

  const label =
    place.formattedAddress?.trim() || place.displayName?.trim() || 'Selected location';

  return {
    latitude: Number(location.lat().toFixed(6)),
    longitude: Number(location.lng().toFixed(6)),
    label,
  };
}

export async function geocodeQueryInKosovo(query: string): Promise<PlaceSelection | null> {
  const trimmed = query.trim();
  if (!trimmed) {
    return null;
  }

  await loadGooglePlaces();
  const geocoder = new google.maps.Geocoder();

  const attempts = [
    `${trimmed}, Kosovo`,
    trimmed,
  ];

  for (const address of attempts) {
    const response = await geocoder.geocode({
      address,
      bounds: KOSOVO_BOUNDS,
      region: 'XK',
    });

    const results = response.results;
    const match = results.find((result) => {
      const location = result.geometry?.location;
      if (!location) {
        return false;
      }
      const lat = location.lat();
      const lng = location.lng();
      return (
        lat >= KOSOVO_BOUNDS.south &&
        lat <= KOSOVO_BOUNDS.north &&
        lng >= KOSOVO_BOUNDS.west &&
        lng <= KOSOVO_BOUNDS.east
      );
    });

    if (match?.geometry?.location) {
      const location = match.geometry.location;
      return {
        latitude: Number(location.lat().toFixed(6)),
        longitude: Number(location.lng().toFixed(6)),
        label: match.formatted_address?.trim() || trimmed,
      };
    }
  }

  return null;
}

export async function reverseGeocodeCoordinates(
  latitude: number,
  longitude: number,
): Promise<string> {
  await loadGooglePlaces();
  const geocoder = new google.maps.Geocoder();
  const response = await geocoder.geocode({
    location: { lat: latitude, lng: longitude },
  });

  const match = response.results[0];
  if (match?.formatted_address) {
    return match.formatted_address;
  }

  return `${latitude.toFixed(5)}, ${longitude.toFixed(5)}`;
}

export function getKosovoMapPickerOptions(): google.maps.MapOptions {
  return {
    ...getPlacesMapOptions(),
    mapTypeControl: false,
    streetViewControl: false,
    fullscreenControl: false,
    zoomControl: true,
    clickableIcons: false,
  };
}
