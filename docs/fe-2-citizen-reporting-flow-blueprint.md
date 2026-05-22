# FE-2 Citizen Reporting Flow Blueprint

## Purpose

This document defines the full implementation blueprint for **Phase FE-2: Citizen Reporting Flow**.

FE-0 established the frontend foundation. FE-1 established the visual and UX system. FE-2 turns the citizen-facing reporting surface into a real mobile-first flow where a citizen can create a structured, geolocated civic issue report.

No implementation should begin until this blueprint is reviewed and approved.

## Phase Goal

Build the citizen report flow end to end:

- Photo capture or upload
- Location capture
- Manual location fallback
- Issue category selection
- Optional AI suggestion display when backend support exists
- Description field
- Review and confirmation
- Submission to backend
- Success/tracking screen
- Recoverable validation and network errors

Primary outcome:

> After FE-2, a citizen should be able to submit a real report from a mobile browser using the backend `POST /api/v1/reports` contract, with no fake upload, fake AI, fake tracking, or fake submission behavior.

## Critical Backend Reality Check

Current backend endpoints:

```text
GET /api/v1/reports
POST /api/v1/reports
```

Current backend `POST /api/v1/reports` accepts structured report data:

- `category`
- `latitude`
- `longitude`
- `source`
- `description`
- `confidence`

Current backend does **not** yet provide:

- Image upload endpoint
- Image storage endpoint
- AI image analysis endpoint
- Report detail endpoint by ID
- Citizen tracking lookup endpoint

Therefore FE-2 should be implemented in two layers:

1. **Fully functional structured report submission** using the current backend.
2. **Prepared image/AI UI and state boundaries** that do not pretend upload or AI analysis works until backend endpoints exist.

No-stub rule:

- If there is no backend upload endpoint, the UI may accept and preview a selected image locally, but it must not claim the image was uploaded.
- If there is no AI endpoint, the UI must not show fake AI suggestions.
- The final submitted backend payload must be real and match the current backend schema.

## Non-Goals

FE-2 will not implement:

- Backend image upload
- Backend AI inference
- Backend persistent image storage
- Google Street View scanning
- Municipality dashboard triage
- Ticket status mutation
- Authentication
- Real citizen tracking from a separate lookup endpoint

FE-2 can prepare the frontend shape for these without faking them.

## User Flow

Primary citizen flow:

```text
/report
  ↓
Step 1: Select or capture photo locally
  ↓
Step 2: Capture browser location or enter manual coordinates
  ↓
Step 3: Choose issue category
  ↓
Step 4: Add optional description
  ↓
Step 5: Review payload
  ↓
Submit to POST /api/v1/reports
  ↓
/report/status/:id
```

Important:

- The image is part of the local review experience in FE-2 unless backend upload exists.
- The submitted backend report is the structured civic issue report.
- The success/tracking page uses the real ID returned by the backend create report response.

## Route Plan

Active routes for FE-2:

```text
/report
/report/status/:id
```

Reserved route:

```text
/report/confirm
```

Implementation decision:

- Prefer a single-page wizard inside `/report` for speed and lower route complexity.
- Use `/report/status/:id` for the real success/tracking screen after submission.
- Do not add `/report/confirm` unless the team decides a separate review route is necessary.

## UX Principles

Citizen reporting must be:

- Fast
- Clear
- Mobile-first
- Forgiving
- Honest about AI and upload limitations
- Accessible on common phone screens

UX rules:

- A citizen should understand why location is needed before granting permission.
- A citizen should be able to continue with manual coordinates if geolocation is denied.
- A citizen should be able to submit without AI assistance.
- A citizen should see exactly what will be submitted.
- Errors should say what went wrong and how to recover.
- No button should look functional if it cannot complete its action.

## Screen: `/report`

Purpose:

- Own the full citizen report creation wizard.

Page sections:

1. Header
2. Progress indicator
3. Photo step
4. Location step
5. Category step
6. Description step
7. Review and submit step

### Step 1: Photo

Build:

- File input for image selection/capture.
- Mobile-friendly `accept="image/*"` and `capture="environment"` where supported.
- Local image preview.
- File metadata display:
  - filename
  - size
  - type
- Remove/change image control.

Validation:

- Accepted file types: image files only.
- Recommended max file size: 8 MB for frontend validation.
- Image is recommended but should not block structured report submission until backend upload is available.

Copy rule:

- Say: "Image selected for local review."
- Do not say: "Image uploaded" unless an upload endpoint exists and succeeds.

### Step 2: Location

Build:

- Explain why location is needed.
- Button to use current location.
- Use existing `useGeolocation`.
- Display captured latitude, longitude, and accuracy.
- Manual coordinate fallback:
  - latitude input
  - longitude input
- Validation for coordinate ranges.

Validation:

- Latitude must be between `-90` and `90`.
- Longitude must be between `-180` and `180`.
- Location is required for submission.

Default context:

- The flow is Prishtina-focused, but users should still submit any valid coordinates.

### Step 3: Category

Build:

- Category selector using all MVP classes:
  - Pothole
  - Garbage or illegal dumping
  - Broken streetlight
  - Blocked sidewalk
  - Damaged sign
  - Other
- Use `IssueCategoryBadge` for visual consistency.
- Cards or segmented options should be touch-friendly.

Validation:

- Category is required.

AI rule:

- If no AI endpoint exists, show a calm note:
  - "AI category suggestion will appear here once image analysis is connected."
- Do not show fake confidence.
- Do not auto-select a category from fake AI.

### Step 4: Description

Build:

- Optional text area.
- Helper copy: "Add context such as lane, nearby landmark, or urgency."
- Character limit matching backend: max 1000 characters.
- Remaining character count.

Validation:

- Description must be at most 1000 characters.

### Step 5: Review And Submit

Build:

- Review card showing:
  - Selected category
  - Location
  - Description
  - Image local preview state
  - AI status: not connected yet, unless endpoint exists
- Submit button.
- Recoverable error state.
- Loading state while submitting.

Submitted payload:

```ts
{
  category: IssueCategory;
  latitude: number;
  longitude: number;
  source: 'citizen';
  description?: string;
  confidence?: number;
}
```

FE-2 default:

- `source` must be `citizen`.
- `confidence` should be omitted unless a real AI endpoint returns a real value.

Success behavior:

- Navigate to `/report/status/:id` using the real backend response ID.

## Screen: `/report/status/:id`

Purpose:

- Give the citizen a real confirmation and tracking ID after submission.

Build:

- Route param: `id`
- Success message
- Tracking ID display
- Explanation of municipal workflow:
  - New
  - Verified
  - Assigned
  - In Progress
  - Resolved
- Link back to create another report
- Link to dashboard for demo/team use if appropriate

Backend limitation:

- Since there is no `GET /api/v1/reports/:id` endpoint yet, this page should not pretend to fetch live report status.
- It can show the submitted ID and the standard workflow explanation.

Copy rule:

- Say: "Your report was submitted. Keep this tracking ID."
- Do not say: "Live status loaded" unless a report detail endpoint exists.

## State Model

Recommended local form state:

```ts
interface ReportDraft {
  imageFile: File | null;
  imagePreviewUrl: string | null;
  category: IssueCategory | null;
  latitude: number | null;
  longitude: number | null;
  locationAccuracy: number | null;
  description: string;
  aiSuggestion: AiSuggestion | null;
}

interface AiSuggestion {
  category: IssueCategory;
  confidence: number;
  explanation?: string;
}
```

Important:

- `aiSuggestion` remains `null` until a real AI endpoint exists.
- Image preview URLs must be revoked when image changes or component unmounts.

## Components To Add

```text
frontend/src/components/reports/ReportProgress.vue
frontend/src/components/reports/PhotoCaptureField.vue
frontend/src/components/reports/LocationCaptureField.vue
frontend/src/components/reports/IssueCategorySelector.vue
frontend/src/components/reports/ReportReviewCard.vue
frontend/src/components/reports/ReportWorkflowTimeline.vue
```

### `ReportProgress.vue`

Purpose:

- Show current report flow progress.

Props:

- `currentStep`
- `steps`

Acceptance:

- Works on mobile.
- Text labels remain visible.
- Does not imply a step is completed unless validation passes.

### `PhotoCaptureField.vue`

Purpose:

- Own local image selection and preview.

Props:

- `modelValue: File | null`

Events:

- `update:modelValue`

Responsibilities:

- Validate image type.
- Validate file size.
- Render preview.
- Render local-only upload limitation copy.

Acceptance:

- No fake upload behavior.
- Selected image preview works.
- User can remove/change image.

### `LocationCaptureField.vue`

Purpose:

- Own geolocation and manual coordinate fallback.

Props:

- `latitude`
- `longitude`
- `accuracy`

Events:

- `update:latitude`
- `update:longitude`
- `update:accuracy`

Responsibilities:

- Trigger browser geolocation.
- Display permission/loading/error states.
- Accept manual coordinate input.

Acceptance:

- User can recover if browser geolocation fails or is denied.

### `IssueCategorySelector.vue`

Purpose:

- Own category selection UI.

Props:

- `modelValue: IssueCategory | null`

Events:

- `update:modelValue`

Acceptance:

- All MVP classes are available.
- Selection is clear and touch-friendly.

### `ReportReviewCard.vue`

Purpose:

- Show exactly what will be submitted.

Props:

- `draft`
- `canSubmit`
- `isSubmitting`
- `error`

Events:

- `submit`

Acceptance:

- Submit button only enabled when required structured fields are valid.
- Review does not claim image upload or AI analysis if unavailable.

### `ReportWorkflowTimeline.vue`

Purpose:

- Explain municipal report lifecycle on the status page.

Props:

- `currentStatus`

Acceptance:

- Shows workflow states clearly.
- Does not claim live status unless backend supports it.

## Files To Add

```text
frontend/src/components/reports/ReportProgress.vue
frontend/src/components/reports/PhotoCaptureField.vue
frontend/src/components/reports/LocationCaptureField.vue
frontend/src/components/reports/IssueCategorySelector.vue
frontend/src/components/reports/ReportReviewCard.vue
frontend/src/components/reports/ReportWorkflowTimeline.vue
frontend/src/pages/citizen/ReportStatusPage.vue
frontend/src/composables/useImagePreview.ts
frontend/src/types/reportDraft.ts
```

## Files To Modify

```text
frontend/src/api/reports.ts
frontend/src/router/index.ts
frontend/src/pages/citizen/CitizenReportPage.vue
frontend/src/types/report.ts
```

Optional if needed:

```text
frontend/src/components/common/AppTextarea.vue
```

## API Updates Needed On Frontend

Current:

```ts
listReports(): Promise<ReportSummary[]>
```

Add:

```ts
createReport(payload: ReportCreatePayload): Promise<ReportSummary>
```

Add types:

```ts
export interface ReportCreatePayload {
  category: IssueCategory;
  latitude: number;
  longitude: number;
  source: 'citizen';
  description?: string;
  confidence?: number;
}
```

Current backend response is compatible with `ReportSummary`.

## Validation Rules

Required to submit:

- Valid latitude
- Valid longitude
- Selected category

Optional:

- Image file
- Description
- AI suggestion

Frontend validation:

- Image must be an image file if selected.
- Image should be 8 MB or smaller.
- Description must be 1000 characters or fewer.
- Latitude must be `-90` to `90`.
- Longitude must be `-180` to `180`.

Submission should be blocked only for invalid required structured fields.

## Error Handling

Error scenarios:

- Geolocation denied
- Geolocation unavailable
- Geolocation timeout
- Invalid manual coordinates
- Invalid file type
- File too large
- Backend validation error
- Network failure

UX requirements:

- Show clear error near the relevant section.
- Preserve user-entered data after errors.
- Allow retry.
- Do not clear image or description after failed submit.

## AI Suggestion Handling

FE-2 should prepare for AI but not fake it.

If no AI endpoint exists:

- Show "AI image analysis is not connected yet."
- Let the user manually select category.
- Submit without `confidence`.

If backend adds AI endpoint before implementation:

- Add an optional `analyzeImage` API function.
- Only show AI suggestion after a real API response.
- Let user override the suggestion.
- Include `confidence` only if the chosen category came from a real AI result or if product decision says to store AI confidence separately.

## No-Stub Rule For FE-2

Allowed:

- Local image preview
- Manual category selection
- Real structured report submission
- Real success screen using backend response ID
- Honest "AI not connected yet" copy
- Honest "image selected locally" copy

Not allowed:

- Fake AI category suggestions
- Fake confidence values
- Fake upload success
- Fake tracking status fetch
- Fake report detail data
- Fake map selection
- Buttons that appear active but do nothing
- Console-only submission
- Lorem ipsum

## Accessibility Requirements

FE-2 must include:

- Labels for all form controls
- Visible focus states
- Error text connected to relevant controls where practical
- Buttons disabled only when necessary
- Keyboard-operable category selection
- Text alternatives for image preview state
- No color-only validation meaning

## Responsive Requirements

Test at:

- 360px mobile width
- 768px tablet width
- 1280px desktop width

Expected behavior:

- Single-column report wizard on mobile.
- Touch targets are comfortable.
- Image preview does not overflow.
- Category selector is easy to tap.
- Review card remains readable.

## Implementation Sequence

1. Add `ReportCreatePayload` and report draft types.
2. Add `createReport` API function.
3. Add `useImagePreview`.
4. Add `AppTextarea` if needed.
5. Add report flow components:
   - `ReportProgress`
   - `PhotoCaptureField`
   - `LocationCaptureField`
   - `IssueCategorySelector`
   - `ReportReviewCard`
   - `ReportWorkflowTimeline`
6. Refactor `CitizenReportPage` into a working single-page wizard.
7. Add `ReportStatusPage`.
8. Add `/report/status/:id` route.
9. Validate form behavior.
10. Run build.
11. Run backend and frontend together.
12. Submit a real report to `POST /api/v1/reports`.
13. Confirm success route receives real ID.

## Verification Plan

Required frontend command:

```bash
cd frontend
npm run build
```

Local integrated verification:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

```bash
cd frontend
npm run dev
```

Manual flow:

1. Open `/report`.
2. Select an image.
3. Use browser location or enter coordinates manually.
4. Select a category.
5. Add optional description.
6. Review payload.
7. Submit.
8. Confirm navigation to `/report/status/:id`.
9. Confirm backend `GET /api/v1/reports` includes the new report.

Expected backend payload example:

```json
{
  "category": "pothole",
  "latitude": 42.6629,
  "longitude": 21.1655,
  "source": "citizen",
  "description": "Large pothole near the right lane."
}
```

## Risks And Mitigations

Risk: Users think the image is uploaded.

Mitigation:

- Copy must clearly say image is selected locally until upload is connected.

Risk: Users think AI analyzed the image.

Mitigation:

- AI area must say analysis is not connected yet unless a real endpoint exists.

Risk: Geolocation fails during demo.

Mitigation:

- Manual coordinate fallback is required.

Risk: Backend returns report but no detail endpoint exists.

Mitigation:

- Status page shows real tracking ID and workflow explanation, not fake live status.

Risk: Flow becomes too long on mobile.

Mitigation:

- Use a progressive single-page layout with clear sections and review card.

## FE-2 Acceptance Criteria

FE-2 is complete when:

- `npm run build` passes.
- `/report` provides a real mobile-first report form.
- A citizen can select an image locally and preview it.
- A citizen can capture or manually enter location.
- A citizen can select any MVP issue category.
- A citizen can add an optional description.
- Submission sends a real `POST /api/v1/reports` request.
- Successful submission navigates to `/report/status/:id` using the real backend response ID.
- No fake AI, upload, tracking, map, or report detail behavior is introduced.
- Errors are recoverable and do not erase user input.

## Approval Gate

If this blueprint is approved, implementation should proceed in the sequence above.

Any change to backend dependency, route structure, or image/AI behavior should be agreed before coding.

