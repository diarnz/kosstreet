# Supabase Storage for report photos

Citizen report photos are uploaded to **Supabase Storage** when configured, so every device can load them via a public HTTPS URL instead of your local `backend/uploads/` folder.

## One-time setup

1. Open your [Supabase project](https://supabase.com/dashboard) → **Storage**.
2. Create a bucket named **`report-images`**.
3. Set the bucket to **Public** (or add a read policy for `reports/*`).
4. Go to **Project Settings → API** and copy the **service_role** key (keep it server-side only).
5. Add to your root `.env`:

```env
# Optional — auto-derived from KOSTREET_DATABASE_URL when using Supabase Postgres
KOSTREET_SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
KOSTREET_SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
KOSTREET_SUPABASE_STORAGE_BUCKET=report-images
```

6. Restart the backend.

On startup, any images still in `backend/uploads/` are uploaded to Supabase automatically. New reports go straight to the bucket.

## API behavior

- The database still stores only the filename in `reports.image_path`.
- API responses return a proxy URL in `image_url`, for example:
  `/api/v1/reports/<report-id>/image`
- The backend serves images from Supabase using the service role key, so the bucket does **not** need to be public.
- If Supabase Storage is not configured, the app falls back to local files served through the same proxy route.
