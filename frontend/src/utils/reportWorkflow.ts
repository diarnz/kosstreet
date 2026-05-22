import type { TicketStatus } from '@/types/report';

export const workflowStatusOrder: TicketStatus[] = [
  'new',
  'verified',
  'assigned',
  'in_progress',
  'resolved',
  'rejected',
];

export const allowedStatusTransitions: Record<TicketStatus, TicketStatus[]> = {
  new: ['verified', 'rejected'],
  verified: ['assigned', 'rejected'],
  assigned: ['in_progress', 'rejected'],
  in_progress: ['resolved', 'rejected'],
  resolved: ['verified'],
  rejected: ['new'],
};

export function getAllowedNextStatuses(status: TicketStatus): TicketStatus[] {
  return allowedStatusTransitions[status];
}

export function requiresWorkflowNote(status: TicketStatus): boolean {
  return status === 'resolved' || status === 'rejected';
}
