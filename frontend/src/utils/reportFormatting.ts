import type { IssueCategory, ReportSource, TicketStatus } from '@/types/report';

export const categoryLabels: Record<IssueCategory, string> = {
  pothole: 'Pothole',
  garbage: 'Garbage',
  broken_streetlight: 'Broken Light',
  blocked_sidewalk: 'Blocked Sidewalk',
  damaged_sign: 'Damaged Sign',
  other: 'Other',
};

export const statusLabels: Record<TicketStatus, string> = {
  new: 'New',
  verified: 'Verified',
  assigned: 'Assigned',
  in_progress: 'In Progress',
  resolved: 'Resolved',
  rejected: 'Rejected',
};

export const statusShortLabels: Record<TicketStatus, string> = {
  new: 'New',
  verified: 'Verify',
  assigned: 'Assign',
  in_progress: 'Work',
  resolved: 'Close',
  rejected: 'Reject',
};

export const sourceLabels: Record<ReportSource, string> = {
  citizen: 'Citizen',
  street_audit: 'AI Street Audit',
};

export function formatDateTime(value: string): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date);
}

export function formatRelativeTime(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  const diffMs = date.getTime() - Date.now();
  const diffMinutes = Math.round(diffMs / 60_000);
  const formatter = new Intl.RelativeTimeFormat(undefined, { numeric: 'auto' });

  if (Math.abs(diffMinutes) < 60) {
    return formatter.format(diffMinutes, 'minute');
  }

  const diffHours = Math.round(diffMinutes / 60);
  if (Math.abs(diffHours) < 24) {
    return formatter.format(diffHours, 'hour');
  }

  const diffDays = Math.round(diffHours / 24);
  if (Math.abs(diffDays) < 7) {
    return formatter.format(diffDays, 'day');
  }

  return new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric' }).format(date);
}

export function formatCoordinates(latitude: number, longitude: number): string {
  return `${latitude.toFixed(5)}, ${longitude.toFixed(5)}`;
}

export function formatConfidence(confidence: number | null | undefined): string {
  if (confidence === null || confidence === undefined) {
    return 'Not available';
  }

  return `${Math.round(confidence * 100)}%`;
}

