import type { DemoDatasetMeta } from '@/types/demo';

export const demoScenario: DemoDatasetMeta & {
  enabledLabel: string;
  durationTarget: string;
  disclaimer: string;
} = {
  id: 'prizren-civic-corridor-demo',
  label: 'Pitch Mode',
  description: 'Prepared frontend records for a reliable KoStreet judging walkthrough.',
  municipality: 'Prizren',
  routeName: 'Prizren old town corridor demo',
  enabledLabel: 'Pitch Mode',
  durationTarget: '3 minutes',
  disclaimer: 'Demo records are frontend fixtures for judging reliability.',
};
