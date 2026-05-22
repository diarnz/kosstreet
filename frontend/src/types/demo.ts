export type DataMode = 'live' | 'demo' | 'mixed';

export interface DemoDatasetMeta {
  id: string;
  label: string;
  description: string;
  municipality: string;
  routeName: string;
}
