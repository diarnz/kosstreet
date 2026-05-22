export type StreetViewTargetSource = 'report' | 'audit_suggestion' | 'audit_run';

export interface StreetViewTarget {
  id: string;
  label: string;
  latitude: number;
  longitude: number;
  heading?: number | null;
  pitch?: number | null;
  description?: string | null;
  source: StreetViewTargetSource;
}

export interface StreetViewLookupResult {
  panorama: google.maps.StreetViewPanoramaData;
  position: google.maps.LatLngLiteral;
}

export interface StreetViewCurrentView {
  latitude: number;
  longitude: number;
  heading: number;
  pitch: number;
}
