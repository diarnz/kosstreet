import { describe, expect, it } from 'vitest';
import {
  buildFrameTileLabel,
  buildRegionTooltipContent,
  formatSeverityLabel,
  getNeonSeverityCircleStyle,
  getSeverityCircleStyle,
  neonLegendSwatchStyle,
  resolveApiAssetUrl,
  regionOverlayPosition,
} from './detectionRegions';

describe('detectionRegions', () => {
  it('resolves relative API asset URLs against the configured base', () => {
    expect(resolveApiAssetUrl('/api/v1/audit-runs/demo/frames/0/image')).toBe(
      'http://localhost:8001/api/v1/audit-runs/demo/frames/0/image',
    );
  });

  it('maps normalized regions to overlay percentages', () => {
    expect(
      regionOverlayPosition({
        center_x: 0.42,
        center_y: 0.68,
        radius: 0.12,
      }),
    ).toEqual({
      centerXPercent: 42,
      centerYPercent: 68,
      radiusPercent: 12,
    });
  });

  it('builds tooltip content from detection metadata', () => {
    const tooltip = buildRegionTooltipContent({
      category: 'Pothole',
      confidence: 0.91,
      description: 'Large pothole in the right lane.',
      severity: 'high',
    });

    expect(tooltip.title).toBe('Pothole · high');
    expect(tooltip.body).toContain('91%');
    expect(tooltip.body).toContain('Large pothole in the right lane.');
  });

  it('builds accessible frame tile labels', () => {
    expect(
      buildFrameTileLabel({
        frameIndex: 4,
        heading: 90,
        isCivicIssue: true,
        category: 'Garbage',
        severity: 'medium',
      }),
    ).toBe('Frame 5, heading 90 degrees, Garbage, medium');
  });

  it('preserves classic circle styles for rollback', () => {
    const classic = getSeverityCircleStyle('high', 'classic');
    expect(classic.stroke).toBe('#ef4444');
    expect(classic.fill).toContain('rgba');
  });

  it('exposes neon styles with translucent fill and breathe range', () => {
    const neon = getNeonSeverityCircleStyle('critical');
    expect(neon.fillOpacity).toBeGreaterThan(0);
    expect(neon.fillOpacity).toBeLessThan(0.5);
    expect(neon.breatheMaxOpacity).toBeGreaterThan(neon.breatheMinOpacity);
    expect(neon.breatheMaxScale).toBeGreaterThan(neon.breatheMinScale);
  });

  it('builds neon legend swatches as solid translucent fills', () => {
    const swatch = neonLegendSwatchStyle('low');
    expect(swatch.borderColor).toBe('transparent');
    expect(swatch.backgroundColor).toContain('rgba');
  });
});
