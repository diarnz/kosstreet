import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '@/pages/HomePage.vue';
import CitizenReportPage from '@/pages/citizen/CitizenReportPage.vue';
import DashboardPage from '@/pages/dashboard/DashboardPage.vue';
import AuditPage from '@/pages/audit/AuditPage.vue';

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomePage },
    { path: '/report', name: 'citizen-report', component: CitizenReportPage },
    { path: '/dashboard', name: 'municipal-dashboard', component: DashboardPage },
    { path: '/audit', name: 'street-audit', component: AuditPage },
  ],
});

