import { resolveApiAssetUrl } from '@/utils/apiAssets';

const prefetchedUrls = new Set<string>();

export function prefetchImageUrl(imageUrl: string): void {
  const resolved = resolveApiAssetUrl(imageUrl);
  if (prefetchedUrls.has(resolved)) {
    return;
  }

  prefetchedUrls.add(resolved);
  const image = new Image();
  image.decoding = 'async';
  image.src = resolved;
}

export function clearPrefetchedImages(): void {
  prefetchedUrls.clear();
}
