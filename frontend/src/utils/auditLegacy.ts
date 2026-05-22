import type { AuditRunSummary } from '@/types/audit';

export function isLegacyAuditRun(
  run: Pick<AuditRunSummary, 'frames_total'>,
  scanPathLength = 0,
): boolean {
  if (run.frames_total < 32) {
    return false;
  }

  if (scanPathLength > 0) {
    return run.frames_total / scanPathLength >= 3.5;
  }

  return run.frames_total >= 32 && run.frames_total % 4 === 0;
}
