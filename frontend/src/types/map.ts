export interface MapPoint {
  id: string;
  latitude: number;
  longitude: number;
}

export interface MapViewport {
  center: {
    latitude: number;
    longitude: number;
  };
  zoom: number;
}

export interface HiddenMapReport {
  id: string;
  reason: 'invalid_coordinates';
}
