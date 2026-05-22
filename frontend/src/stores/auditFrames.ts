import { defineStore } from 'pinia';
import { getAuditFrame, listAuditFrames } from '@/api/auditFrames';
import type { AuditFrameDetail, AuditFrameSummary } from '@/types/auditFrame';

interface AuditFramesState {
  framesByRunId: Record<string, AuditFrameSummary[]>;
  frameDetailsByKey: Record<string, AuditFrameDetail>;
  loadingByRunId: Record<string, boolean>;
  errorByRunId: Record<string, string | null>;
  detailLoadingByKey: Record<string, boolean>;
  detailErrorByKey: Record<string, string | null>;
}

function frameDetailKey(runId: string, frameIndex: number): string {
  return `${runId}:${frameIndex}`;
}

function getErrorMessage(error: unknown, fallback: string): string {
  return error instanceof Error ? error.message : fallback;
}

export const useAuditFramesStore = defineStore('auditFrames', {
  state: (): AuditFramesState => ({
    framesByRunId: {},
    frameDetailsByKey: {},
    loadingByRunId: {},
    errorByRunId: {},
    detailLoadingByKey: {},
    detailErrorByKey: {},
  }),
  getters: {
    framesForRun:
      (state) =>
      (runId: string | null): AuditFrameSummary[] =>
        runId ? state.framesByRunId[runId] ?? [] : [],
    isLoadingForRun:
      (state) =>
      (runId: string | null): boolean =>
        runId ? state.loadingByRunId[runId] ?? false : false,
    errorForRun:
      (state) =>
      (runId: string | null): string | null =>
        runId ? state.errorByRunId[runId] ?? null : null,
    frameDetail:
      (state) =>
      (runId: string | null, frameIndex: number | null): AuditFrameDetail | null => {
        if (!runId || frameIndex === null) {
          return null;
        }

        return state.frameDetailsByKey[frameDetailKey(runId, frameIndex)] ?? null;
      },
    isDetailLoading:
      (state) =>
      (runId: string | null, frameIndex: number | null): boolean => {
        if (!runId || frameIndex === null) {
          return false;
        }

        return state.detailLoadingByKey[frameDetailKey(runId, frameIndex)] ?? false;
      },
    detailError:
      (state) =>
      (runId: string | null, frameIndex: number | null): string | null => {
        if (!runId || frameIndex === null) {
          return null;
        }

        return state.detailErrorByKey[frameDetailKey(runId, frameIndex)] ?? null;
      },
  },
  actions: {
    async fetchForRun(runId: string): Promise<AuditFrameSummary[]> {
      this.loadingByRunId[runId] = true;
      this.errorByRunId[runId] = null;

      try {
        const frames = await listAuditFrames(runId);
        this.framesByRunId[runId] = frames;
        return frames;
      } catch (error) {
        this.errorByRunId[runId] = getErrorMessage(
          error,
          'Could not load analyzed frames for this audit run.',
        );
        return [];
      } finally {
        this.loadingByRunId[runId] = false;
      }
    },
    async fetchFrameDetail(runId: string, frameIndex: number): Promise<AuditFrameDetail | null> {
      const key = frameDetailKey(runId, frameIndex);
      this.detailLoadingByKey[key] = true;
      this.detailErrorByKey[key] = null;

      try {
        const frame = await getAuditFrame(runId, frameIndex);
        this.frameDetailsByKey[key] = frame;
        return frame;
      } catch (error) {
        this.detailErrorByKey[key] = getErrorMessage(
          error,
          'Could not load the selected analyzed frame.',
        );
        return null;
      } finally {
        this.detailLoadingByKey[key] = false;
      }
    },
  },
});
