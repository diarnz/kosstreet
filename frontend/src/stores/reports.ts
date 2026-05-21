import { defineStore } from 'pinia';
import type { ReportSummary } from '@/types/report';

interface ReportsState {
  reports: ReportSummary[];
}

export const useReportsStore = defineStore('reports', {
  state: (): ReportsState => ({
    reports: [],
  }),
});

