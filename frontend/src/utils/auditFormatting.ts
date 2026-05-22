import type { AuditRunStatus } from '@/types/audit';

export const auditRunStatusLabels: Record<AuditRunStatus, string> = {
  queued: 'Queued',
  running: 'Running',
  completed: 'Completed',
  failed: 'Failed',
};

export const auditRunStatusDescriptions: Record<AuditRunStatus, string> = {
  queued: 'Waiting for backend orchestration to start the AI street audit pipeline.',
  running: 'Backend and AI services are processing the selected route.',
  completed: 'Backend marked the audit run complete. Review any persisted AI suggestions returned for this run.',
  failed: 'Backend marked the audit run failed. Review backend/AI logs before retrying.',
};

export function formatAuditDateTime(value: string): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date);
}
