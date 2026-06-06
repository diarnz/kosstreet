<template>
  <div class="admin-page">
    <header class="admin-page__header">
      <div>
        <p class="admin-page__eyebrow">Hidden admin</p>
        <h1>Admin database</h1>
        <p class="admin-page__sub">
          Manage reports and street audit data with previews before you hide or delete anything.
        </p>
      </div>
      <AppButton v-if="isAuthenticated" variant="ghost" size="sm" @click="logout">
        Lock panel
      </AppButton>
    </header>

    <GlassPanel v-if="!isAuthenticated" label="Admin key" class="admin-page__gate">
      <p class="admin-page__hint">Enter your <code>KOSTREET_ADMIN_SECRET</code> from <code>.env</code>.</p>
      <form class="admin-page__gate-form" @submit.prevent="unlock">
        <input
          v-model="adminKeyInput"
          class="admin-page__input"
          type="password"
          placeholder="Admin secret"
          autocomplete="off"
        />
        <AppButton type="submit" :disabled="!adminKeyInput.trim()">Unlock</AppButton>
      </form>
      <p v-if="authError" class="admin-page__error">{{ authError }}</p>
    </GlassPanel>

    <template v-else>
      <nav class="admin-page__tabs" aria-label="Admin sections">
        <button
          type="button"
          class="admin-page__tab"
          :class="{ 'admin-page__tab--active': activeTab === 'reports' }"
          @click="activeTab = 'reports'"
        >
          Reports
        </button>
        <button
          type="button"
          class="admin-page__tab"
          :class="{ 'admin-page__tab--active': activeTab === 'audit' }"
          @click="switchToAudit"
        >
          Street audit
        </button>
      </nav>

      <GlassPanel v-if="error" label="Error">
        <p class="admin-page__error">{{ error }}</p>
        <AppButton variant="secondary" size="sm" @click="retryActiveTab">Retry</AppButton>
      </GlassPanel>

      <template v-if="activeTab === 'reports'">
      <GlassPanel label="Create report" class="admin-page__create">
        <form class="admin-page__form-grid" @submit.prevent="createReport">
          <label>
            Category
            <select v-model="createForm.category" class="admin-page__input">
              <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
            </select>
          </label>
          <label>
            Source
            <select v-model="createForm.source" class="admin-page__input">
              <option value="citizen">citizen</option>
              <option value="street_audit">street_audit</option>
            </select>
          </label>
          <label>
            Latitude
            <input v-model.number="createForm.latitude" class="admin-page__input" type="number" step="any" />
          </label>
          <label>
            Longitude
            <input v-model.number="createForm.longitude" class="admin-page__input" type="number" step="any" />
          </label>
          <label class="admin-page__span-2">
            Description
            <input v-model="createForm.description" class="admin-page__input" type="text" />
          </label>
          <div class="admin-page__actions">
            <AppButton type="submit" :disabled="isSaving">Add report</AppButton>
          </div>
        </form>
      </GlassPanel>

      <GlassPanel label="All reports" padding="sm">
        <div class="admin-page__toolbar">
          <span>{{ reports.length }} total</span>
          <span>{{ visibleCount }} visible on dashboard</span>
          <AppButton variant="secondary" size="sm" :disabled="isLoading" @click="loadReports">
            {{ isLoading ? 'Loading…' : 'Refresh' }}
          </AppButton>
        </div>

        <div v-if="isLoading && reports.length === 0" class="admin-page__empty">Loading reports…</div>
        <div v-else-if="reports.length === 0" class="admin-page__empty">No reports in the database.</div>

        <div v-else class="admin-page__table-wrap">
          <table class="admin-page__table">
            <thead>
              <tr>
                <th>Preview</th>
                <th>Visible</th>
                <th>Category</th>
                <th>Status</th>
                <th>Source</th>
                <th>Location</th>
                <th>Description</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="report in reports"
                :key="report.id"
                :class="{ 'admin-page__row--hidden': report.is_visible === false }"
              >
                <td>
                  <img
                    v-if="report.image_url"
                    :src="report.image_url"
                    alt="Report photo"
                    class="admin-page__thumb"
                    loading="lazy"
                  />
                  <span v-else class="admin-page__no-thumb">—</span>
                </td>
                <td>
                  <button
                    class="admin-page__toggle"
                    :class="{ 'admin-page__toggle--on': report.is_visible !== false }"
                    type="button"
                    :disabled="togglingId === report.id"
                    @click="toggleVisibility(report)"
                  >
                    {{ report.is_visible === false ? 'Hidden' : 'Shown' }}
                  </button>
                </td>
                <td>{{ report.category }}</td>
                <td>{{ report.status }}</td>
                <td>{{ report.source }}</td>
                <td>{{ report.latitude.toFixed(4) }}, {{ report.longitude.toFixed(4) }}</td>
                <td class="admin-page__desc">{{ report.description || '—' }}</td>
                <td>{{ formatDate(report.created_at) }}</td>
                <td>
                  <AppButton variant="ghost" size="sm" @click="startEdit(report)">Edit</AppButton>
                  <AppButton
                    variant="ghost"
                    size="sm"
                    :disabled="deletingId === report.id"
                    @click="removeReport(report.id)"
                  >
                    Delete
                  </AppButton>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </GlassPanel>

      <GlassPanel v-if="editingReport" label="Edit report" class="admin-page__edit">
        <form class="admin-page__form-grid" @submit.prevent="saveEdit">
          <label>
            Category
            <select v-model="editForm.category" class="admin-page__input">
              <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
            </select>
          </label>
          <label>
            Status
            <select v-model="editForm.status" class="admin-page__input">
              <option v-for="st in statuses" :key="st" :value="st">{{ st }}</option>
            </select>
          </label>
          <label>
            Source
            <select v-model="editForm.source" class="admin-page__input">
              <option value="citizen">citizen</option>
              <option value="street_audit">street_audit</option>
            </select>
          </label>
          <label>
            Visible on dashboard
            <select v-model="editForm.is_visible" class="admin-page__input">
              <option :value="true">Yes</option>
              <option :value="false">No</option>
            </select>
          </label>
          <label>
            Latitude
            <input v-model.number="editForm.latitude" class="admin-page__input" type="number" step="any" />
          </label>
          <label>
            Longitude
            <input v-model.number="editForm.longitude" class="admin-page__input" type="number" step="any" />
          </label>
          <label class="admin-page__span-2">
            Description
            <input v-model="editForm.description" class="admin-page__input" type="text" />
          </label>
          <div class="admin-page__actions">
            <AppButton type="submit" :disabled="isSaving">Save changes</AppButton>
            <AppButton variant="ghost" type="button" @click="cancelEdit">Cancel</AppButton>
          </div>
        </form>
      </GlassPanel>
      </template>

      <template v-else>
        <GlassPanel label="Audit runs" padding="sm">
          <div class="admin-page__toolbar">
            <span>{{ auditRuns.length }} runs</span>
            <span>{{ visibleAuditCount }} visible on /audit</span>
            <AppButton variant="secondary" size="sm" :disabled="auditLoading" @click="loadAuditRuns">
              {{ auditLoading ? 'Loading…' : 'Refresh' }}
            </AppButton>
          </div>

          <div v-if="auditLoading && auditRuns.length === 0" class="admin-page__empty">Loading audit runs…</div>
          <div v-else-if="auditRuns.length === 0" class="admin-page__empty">No audit runs in the database.</div>

          <div v-else class="admin-page__run-list">
            <article
              v-for="run in auditRuns"
              :key="run.id"
              class="admin-page__run-card"
              :class="{ 'admin-page__run-card--hidden': run.is_visible === false }"
            >
              <header class="admin-page__run-header">
                <div>
                  <h2>{{ run.route_name }}</h2>
                  <p class="admin-page__run-meta">
                    {{ run.status }} · {{ run.suggestion_count }} suggestions ·
                    {{ run.civic_frame_count }} civic frames
                  </p>
                </div>
                <div class="admin-page__run-actions">
                  <button
                    class="admin-page__toggle"
                    :class="{ 'admin-page__toggle--on': run.is_visible !== false }"
                    type="button"
                    :disabled="auditTogglingId === run.id"
                    @click="toggleAuditRunVisibility(run)"
                  >
                    {{ run.is_visible === false ? 'Hidden' : 'Shown' }}
                  </button>
                  <AppButton variant="secondary" size="sm" @click="toggleRunExpanded(run.id)">
                    {{ expandedRunId === run.id ? 'Collapse' : 'Preview frames' }}
                  </AppButton>
                  <AppButton
                    variant="ghost"
                    size="sm"
                    :disabled="deletingAuditRunId === run.id"
                    @click="removeAuditRun(run.id)"
                  >
                    Delete run
                  </AppButton>
                </div>
              </header>

              <div v-if="expandedRunId === run.id" class="admin-page__run-body">
                <p v-if="runContentLoading[run.id]" class="admin-page__empty">Loading frames…</p>
                <template v-else-if="runContentById[run.id]">
                  <section v-if="runContentById[run.id].suggestions.length" class="admin-page__media-section">
                    <h3>Suggestions</h3>
                    <div class="admin-page__media-grid">
                      <figure
                        v-for="suggestion in runContentById[run.id].suggestions"
                        :key="suggestion.id"
                        class="admin-page__media-card"
                        :class="{ 'admin-page__media-card--hidden': suggestion.is_visible === false }"
                      >
                        <img
                          v-if="suggestion.frame_image_url"
                          :src="suggestion.frame_image_url"
                          :alt="suggestion.description || suggestion.category"
                          class="admin-page__media-img"
                          loading="lazy"
                        />
                        <figcaption>
                          <strong>{{ suggestion.category }}</strong>
                          <span>{{ suggestion.description || 'No description' }}</span>
                          <div class="admin-page__media-actions">
                            <button
                              class="admin-page__toggle"
                              :class="{ 'admin-page__toggle--on': suggestion.is_visible !== false }"
                              type="button"
                              @click="toggleSuggestionVisibility(suggestion)"
                            >
                              {{ suggestion.is_visible === false ? 'Hidden' : 'Shown' }}
                            </button>
                            <AppButton
                              variant="ghost"
                              size="sm"
                              @click="removeSuggestion(suggestion.id, run.id)"
                            >
                              Delete
                            </AppButton>
                          </div>
                        </figcaption>
                      </figure>
                    </div>
                  </section>

                  <section v-if="runContentById[run.id].frames.length" class="admin-page__media-section">
                    <h3>Detected frames</h3>
                    <div class="admin-page__media-grid">
                      <figure
                        v-for="frame in runContentById[run.id].frames"
                        :key="`${run.id}-${frame.frame_index}`"
                        class="admin-page__media-card"
                      >
                        <img
                          :src="frame.frame_image_url"
                          :alt="frame.description || `Frame ${frame.frame_index}`"
                          class="admin-page__media-img"
                          loading="lazy"
                        />
                        <figcaption>
                          <strong>Frame {{ frame.frame_index }}</strong>
                          <span>{{ frame.category || 'no issue' }} · {{ frame.description || '—' }}</span>
                        </figcaption>
                      </figure>
                    </div>
                  </section>

                  <p
                    v-if="
                      !runContentById[run.id].suggestions.length &&
                      !runContentById[run.id].frames.length
                    "
                    class="admin-page__empty"
                  >
                    No preview images for this run yet.
                  </p>
                </template>
              </div>
            </article>
          </div>
        </GlassPanel>
      </template>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import AppButton from '@/components/common/AppButton.vue';
import GlassPanel from '@/components/common/GlassPanel.vue';
import {
  adminDeleteAuditRun,
  adminDeleteAuditSuggestion,
  adminGetAuditRunContent,
  adminListAuditRuns,
  adminUpdateAuditRun,
  adminUpdateAuditSuggestion,
  type AdminAuditRunContent,
  type AdminAuditRunSummary,
} from '@/api/adminAudit';
import {
  adminCreateReport,
  adminDeleteReport,
  adminListReports,
  adminUpdateReport,
  clearStoredAdminKey,
  getStoredAdminKey,
  setStoredAdminKey,
} from '@/api/adminReports';
import type { AuditSuggestion } from '@/types/detection';
import type { IssueCategory, ReportSummary, TicketStatus } from '@/types/report';

type AdminTab = 'reports' | 'audit';

const categories: IssueCategory[] = [
  'pothole',
  'garbage',
  'broken_streetlight',
  'blocked_sidewalk',
  'damaged_sign',
  'other',
];

const statuses: TicketStatus[] = [
  'new',
  'verified',
  'assigned',
  'in_progress',
  'resolved',
  'rejected',
];

const adminKey = ref(getStoredAdminKey());
const adminKeyInput = ref('');
const activeTab = ref<AdminTab>('reports');
const isAuthenticated = computed(() => Boolean(adminKey.value));
const authError = ref<string | null>(null);
const reports = ref<ReportSummary[]>([]);
const auditRuns = ref<AdminAuditRunSummary[]>([]);
const runContentById = ref<Record<string, AdminAuditRunContent>>({});
const runContentLoading = ref<Record<string, boolean>>({});
const expandedRunId = ref<string | null>(null);
const isLoading = ref(false);
const auditLoading = ref(false);
const auditTogglingId = ref<string | null>(null);
const deletingAuditRunId = ref<string | null>(null);
const isSaving = ref(false);
const error = ref<string | null>(null);
const togglingId = ref<string | null>(null);
const deletingId = ref<string | null>(null);
const editingReport = ref<ReportSummary | null>(null);

const createForm = reactive({
  category: 'pothole' as IssueCategory,
  source: 'citizen' as 'citizen' | 'street_audit',
  latitude: 42.6629,
  longitude: 21.1655,
  description: '',
});

const editForm = reactive({
  category: 'pothole' as IssueCategory,
  status: 'new' as TicketStatus,
  source: 'citizen' as 'citizen' | 'street_audit',
  latitude: 0,
  longitude: 0,
  description: '',
  is_visible: true,
});

const visibleCount = computed(
  () => reports.value.filter((report) => report.is_visible !== false).length,
);

const visibleAuditCount = computed(
  () => auditRuns.value.filter((run) => run.is_visible !== false).length,
);

function formatDate(value: string): string {
  return new Date(value).toLocaleString();
}

async function loadReports() {
  if (!adminKey.value) return;
  isLoading.value = true;
  error.value = null;
  try {
    reports.value = await adminListReports(adminKey.value);
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not load reports';
  } finally {
    isLoading.value = false;
  }
}

async function loadAuditRuns() {
  if (!adminKey.value) return;
  auditLoading.value = true;
  error.value = null;
  try {
    auditRuns.value = await adminListAuditRuns(adminKey.value);
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not load audit runs';
  } finally {
    auditLoading.value = false;
  }
}

async function loadRunContent(runId: string) {
  if (!adminKey.value || runContentById.value[runId]) return;
  runContentLoading.value = { ...runContentLoading.value, [runId]: true };
  try {
    runContentById.value = {
      ...runContentById.value,
      [runId]: await adminGetAuditRunContent(adminKey.value, runId),
    };
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not load audit previews';
  } finally {
    runContentLoading.value = { ...runContentLoading.value, [runId]: false };
  }
}

async function switchToAudit() {
  activeTab.value = 'audit';
  if (auditRuns.value.length === 0) {
    await loadAuditRuns();
  }
}

function retryActiveTab() {
  if (activeTab.value === 'audit') {
    void loadAuditRuns();
    return;
  }
  void loadReports();
}

async function toggleRunExpanded(runId: string) {
  if (expandedRunId.value === runId) {
    expandedRunId.value = null;
    return;
  }
  expandedRunId.value = runId;
  await loadRunContent(runId);
}

async function unlock() {
  authError.value = null;
  const key = adminKeyInput.value.trim();
  if (!key) return;
  try {
    await adminListReports(key);
    adminKey.value = key;
    setStoredAdminKey(key);
    adminKeyInput.value = '';
    await loadReports();
  } catch (err) {
    authError.value = err instanceof Error ? err.message : 'Invalid admin key';
  }
}

function logout() {
  adminKey.value = '';
  clearStoredAdminKey();
  reports.value = [];
  auditRuns.value = [];
  runContentById.value = {};
  expandedRunId.value = null;
  editingReport.value = null;
}

async function toggleVisibility(report: ReportSummary) {
  if (!adminKey.value) return;
  togglingId.value = report.id;
  try {
    const updated = await adminUpdateReport(adminKey.value, report.id, {
      is_visible: report.is_visible === false,
    });
    reports.value = reports.value.map((item) =>
      item.id === report.id
        ? {
            ...item,
            is_visible: updated.is_visible,
            status: updated.status,
            category: updated.category,
            description: updated.description,
          }
        : item,
    );
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not update visibility';
  } finally {
    togglingId.value = null;
  }
}

async function createReport() {
  if (!adminKey.value) return;
  isSaving.value = true;
  error.value = null;
  try {
    const created = await adminCreateReport(adminKey.value, {
      category: createForm.category,
      source: createForm.source,
      latitude: createForm.latitude,
      longitude: createForm.longitude,
      description: createForm.description || undefined,
    });
    reports.value = [created, ...reports.value];
    createForm.description = '';
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not create report';
  } finally {
    isSaving.value = false;
  }
}

function startEdit(report: ReportSummary) {
  editingReport.value = report;
  editForm.category = report.category;
  editForm.status = report.status;
  editForm.source = report.source;
  editForm.latitude = report.latitude;
  editForm.longitude = report.longitude;
  editForm.description = report.description ?? '';
  editForm.is_visible = report.is_visible !== false;
}

function cancelEdit() {
  editingReport.value = null;
}

async function saveEdit() {
  if (!adminKey.value || !editingReport.value) return;
  isSaving.value = true;
  error.value = null;
  try {
    const updated = await adminUpdateReport(adminKey.value, editingReport.value.id, {
      category: editForm.category,
      status: editForm.status,
      source: editForm.source,
      latitude: editForm.latitude,
      longitude: editForm.longitude,
      description: editForm.description,
      is_visible: editForm.is_visible,
    });
    reports.value = reports.value.map((item) =>
      item.id === updated.id
        ? {
            id: updated.id,
            category: updated.category,
            status: updated.status,
            latitude: updated.latitude,
            longitude: updated.longitude,
            source: updated.source,
            description: updated.description,
            confidence: updated.confidence,
            is_visible: updated.is_visible,
            created_at: updated.created_at,
          }
        : item,
    );
    editingReport.value = null;
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not save report';
  } finally {
    isSaving.value = false;
  }
}

async function toggleAuditRunVisibility(run: AdminAuditRunSummary) {
  if (!adminKey.value) return;
  auditTogglingId.value = run.id;
  try {
    const updated = await adminUpdateAuditRun(adminKey.value, run.id, {
      is_visible: run.is_visible === false,
    });
    auditRuns.value = auditRuns.value.map((item) =>
      item.id === run.id ? { ...item, is_visible: updated.is_visible } : item,
    );
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not update audit run visibility';
  } finally {
    auditTogglingId.value = null;
  }
}

async function toggleSuggestionVisibility(suggestion: AuditSuggestion) {
  if (!adminKey.value) return;
  try {
    const updated = await adminUpdateAuditSuggestion(adminKey.value, suggestion.id, {
      is_visible: suggestion.is_visible === false,
    });
    const content = runContentById.value[suggestion.audit_run_id];
    if (!content) return;
    runContentById.value = {
      ...runContentById.value,
      [suggestion.audit_run_id]: {
        ...content,
        suggestions: content.suggestions.map((item) =>
          item.id === suggestion.id ? { ...item, is_visible: updated.is_visible } : item,
        ),
      },
    };
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not update suggestion visibility';
  }
}

async function removeAuditRun(runId: string) {
  if (!adminKey.value) return;
  if (!window.confirm('Delete this audit run and all its frames/suggestions?')) return;
  deletingAuditRunId.value = runId;
  error.value = null;
  try {
    await adminDeleteAuditRun(adminKey.value, runId);
    auditRuns.value = auditRuns.value.filter((run) => run.id !== runId);
    if (expandedRunId.value === runId) {
      expandedRunId.value = null;
    }
    const nextContent = { ...runContentById.value };
    delete nextContent[runId];
    runContentById.value = nextContent;
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not delete audit run';
  } finally {
    deletingAuditRunId.value = null;
  }
}

async function removeSuggestion(suggestionId: string, runId: string) {
  if (!adminKey.value) return;
  if (!window.confirm('Delete this audit suggestion?')) return;
  error.value = null;
  try {
    await adminDeleteAuditSuggestion(adminKey.value, suggestionId);
    const content = runContentById.value[runId];
    if (content) {
      runContentById.value = {
        ...runContentById.value,
        [runId]: {
          ...content,
          suggestions: content.suggestions.filter((item) => item.id !== suggestionId),
        },
      };
    }
    auditRuns.value = auditRuns.value.map((run) =>
      run.id === runId
        ? { ...run, suggestion_count: Math.max(0, run.suggestion_count - 1) }
        : run,
    );
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not delete suggestion';
  }
}

async function removeReport(reportId: string) {
  if (!adminKey.value) return;
  if (!window.confirm('Delete this report permanently?')) return;
  deletingId.value = reportId;
  error.value = null;
  try {
    await adminDeleteReport(adminKey.value, reportId);
    reports.value = reports.value.filter((report) => report.id !== reportId);
    if (editingReport.value?.id === reportId) {
      editingReport.value = null;
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not delete report';
  } finally {
    deletingId.value = null;
  }
}

onMounted(async () => {
  if (adminKey.value) {
    await loadReports();
  }
});
</script>

<style scoped>
.admin-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--space-6) var(--space-4) var(--space-10);
  display: grid;
  gap: var(--space-5);
}

.admin-page__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-4);
}

.admin-page__eyebrow {
  margin: 0 0 var(--space-1);
  font-size: 0.75rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.admin-page h1 {
  margin: 0;
}

.admin-page__sub,
.admin-page__hint {
  margin: var(--space-2) 0 0;
  color: var(--color-text-muted);
}

.admin-page__gate-form,
.admin-page__form-grid {
  display: grid;
  gap: var(--space-3);
}

.admin-page__form-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.admin-page__span-2 {
  grid-column: span 2;
}

.admin-page__gate-form {
  grid-template-columns: 1fr auto;
  align-items: end;
}

.admin-page__input {
  width: 100%;
  margin-top: var(--space-1);
  padding: 0.55rem 0.75rem;
  border: 1px solid rgba(47, 93, 80, 0.18);
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.72);
}

label {
  display: block;
  font-size: 0.85rem;
}

.admin-page__toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  align-items: center;
  margin-bottom: var(--space-3);
  color: var(--color-text-muted);
  font-size: 0.9rem;
}

.admin-page__table-wrap {
  overflow-x: auto;
}

.admin-page__table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
}

.admin-page__table th,
.admin-page__table td {
  padding: 0.65rem 0.5rem;
  border-bottom: 1px solid rgba(47, 93, 80, 0.12);
  text-align: left;
  vertical-align: top;
}

.admin-page__desc {
  max-width: 220px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.admin-page__row--hidden {
  opacity: 0.55;
}

.admin-page__toggle {
  border: 1px solid rgba(47, 93, 80, 0.25);
  border-radius: 999px;
  padding: 0.2rem 0.65rem;
  font-size: 0.75rem;
  background: rgba(255, 255, 255, 0.7);
  cursor: pointer;
}

.admin-page__toggle--on {
  background: rgba(47, 93, 80, 0.12);
  border-color: rgba(47, 93, 80, 0.45);
}

.admin-page__actions {
  grid-column: span 2;
  display: flex;
  gap: var(--space-2);
}

.admin-page__error {
  color: #9b2c2c;
  margin: var(--space-2) 0 0;
}

.admin-page__empty {
  padding: var(--space-4);
  color: var(--color-text-muted);
}

.admin-page__tabs {
  display: flex;
  gap: var(--space-2);
}

.admin-page__tab {
  border: 1px solid rgba(47, 93, 80, 0.2);
  border-radius: 999px;
  padding: 0.45rem 1rem;
  background: rgba(255, 255, 255, 0.55);
  cursor: pointer;
}

.admin-page__tab--active {
  background: rgba(47, 93, 80, 0.14);
  border-color: rgba(47, 93, 80, 0.45);
}

.admin-page__thumb {
  width: 56px;
  height: 56px;
  object-fit: cover;
  border-radius: var(--radius-sm);
  border: 1px solid rgba(47, 93, 80, 0.15);
}

.admin-page__no-thumb {
  color: var(--color-text-muted);
}

.admin-page__run-list {
  display: grid;
  gap: var(--space-4);
}

.admin-page__run-card {
  border: 1px solid rgba(47, 93, 80, 0.14);
  border-radius: var(--radius-lg);
  padding: var(--space-3);
  background: rgba(255, 255, 255, 0.45);
}

.admin-page__run-card--hidden {
  opacity: 0.6;
}

.admin-page__run-header {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  align-items: flex-start;
}

.admin-page__run-header h2 {
  margin: 0;
  font-size: 1rem;
}

.admin-page__run-meta {
  margin: var(--space-1) 0 0;
  color: var(--color-text-muted);
  font-size: 0.85rem;
}

.admin-page__run-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  align-items: center;
}

.admin-page__run-body {
  margin-top: var(--space-4);
  padding-top: var(--space-3);
  border-top: 1px solid rgba(47, 93, 80, 0.12);
}

.admin-page__media-section h3 {
  margin: 0 0 var(--space-3);
  font-size: 0.9rem;
}

.admin-page__media-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: var(--space-3);
}

.admin-page__media-card {
  margin: 0;
  border: 1px solid rgba(47, 93, 80, 0.14);
  border-radius: var(--radius-md);
  overflow: hidden;
  background: rgba(255, 255, 255, 0.7);
}

.admin-page__media-card--hidden {
  opacity: 0.55;
}

.admin-page__media-img {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  display: block;
  background: rgba(47, 93, 80, 0.06);
}

.admin-page__media-card figcaption {
  display: grid;
  gap: 0.35rem;
  padding: 0.55rem 0.65rem 0.7rem;
  font-size: 0.78rem;
}

.admin-page__media-card strong {
  text-transform: capitalize;
}

.admin-page__media-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-top: 0.25rem;
}
</style>
