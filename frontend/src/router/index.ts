import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '@/pages/HomePage.vue';
import CitizenReportPage from '@/pages/citizen/CitizenReportPage.vue';
import ReportStatusPage from '@/pages/citizen/ReportStatusPage.vue';
import DashboardPage from '@/pages/dashboard/DashboardPage.vue';
import AuditPage from '@/pages/audit/AuditPage.vue';
import AuditRunDetailPage from '@/pages/audit/AuditRunDetailPage.vue';
import AuditSuggestionDetailPage from '@/pages/audit/AuditSuggestionDetailPage.vue';
import ReportsAdminPage from '@/pages/admin/ReportsAdminPage.vue';
import { useUiStore } from '@/stores/ui';

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomePage },
    { path: '/report', name: 'citizen-report', component: CitizenReportPage },
    { path: '/report/status/:id', name: 'report-status', component: ReportStatusPage },
    { path: '/dashboard', name: 'municipal-dashboard', component: DashboardPage },
    { path: '/audit', name: 'street-audit', component: AuditPage },
    {
      path: '/audit/suggestions/:suggestionId',
      name: 'street-audit-suggestion-detail',
      component: AuditSuggestionDetailPage,
    },
    { path: '/audit/:runId', name: 'street-audit-run-detail', component: AuditRunDetailPage },
    {
      path: '/__kostreet-admin/reports',
      name: 'reports-admin',
      component: ReportsAdminPage,
    },
  ],
});

router.beforeEach((to) => {
  const uiStore = useUiStore();
  const demoQuery = Array.isArray(to.query.demo) ? to.query.demo[0] : to.query.demo;

  if (demoQuery === '1') {
    uiStore.setDemoMode(true);
    return;
  }

  if (demoQuery === '0') {
    uiStore.setDemoMode(false);
  }
});
