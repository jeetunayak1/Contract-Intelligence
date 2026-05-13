# PR Context: Dynamic SOW Parsing, Gemini Metadata, UI Sync, and Firestore Upload Safety

## Branch
- `feature/dynamic-sow-parsing-ui-sync`

## Pull Request
- Create PR: https://github.com/jeetunayak1/Contract-Intelligence/pull/new/feature/dynamic-sow-parsing-ui-sync

## Summary

This change set improves the backend SOW ingestion flow and fixes multiple issues discovered during end-to-end testing with the frontend UI.

The main goals of this work were:

1. make Gemini parsing output easier to inspect and debug
2. align persisted SOW data with the normalized LLM output
3. make action generation less static and more data-driven
4. prevent newly uploaded SOWs from replacing older Firestore records
5. fix the situation where the UI appeared to show a previous SOW response after uploading a new file

---

## Problems Observed

### 1. LLM output looked correct, but UI data looked wrong
During testing, the Gemini response inside `llm_metadata` appeared correct, but the UI still rendered incorrect or stale-looking SOW data.

### 2. Different SOW uploads produced very similar downstream behavior
Even when different documents were uploaded, the action center and review outputs often looked too similar.

### 3. Uploading a new SOW replaced an older Firestore record
If the same `sow_number` was reused, the backend generated the same SOW `_id`, so the save logic updated the existing Firestore document instead of creating a new one.

### 4. UI seemed to keep showing the previous SOW response
Because uploads were overwriting the same persisted record, the frontend list/dashboard behavior looked like the previous SOW response was still being shown.

---

## Root Causes

## A. Persisted SOW construction path was diverging from the normalized LLM output
The ingestion path stored `llm_metadata`, but the final SOW document could still be built from an intermediate parsed structure instead of the normalized response used for debugging.

## B. SOW IDs were not unique per upload
`create_sow_document()` defaulted to:

```python
_id = f"SOW-{sow_number}"
```

That meant uploads using the same `sow_number` pointed to the same Firestore document.

## C. Save logic intentionally updated an existing document when the `_id` already existed
The backend save flow checked for an existing document and updated it. That behavior is valid, but because `_id` was reused, uploads collided.

## D. Some risk/action generation defaults were overly static
Several upstream signals created similarly shaped outputs, which contributed to repeated-looking action items.

---

## Key Changes Implemented

## 1. Added richer Gemini metadata for debugging
File:
- `backend/app/agents/ingestion_agent.py`

Gemini success-path metadata now includes:
- `response_text`
- `response_preview`
- `parsed_response`
- `normalized_response`

This helps compare:
- raw Gemini output
- parsed JSON extracted from the model response
- normalized data actually intended for downstream use

This is useful when investigating whether the model output is different but the saved/UI data is still converging.

---

## 2. Synced persisted SOW building with normalized LLM output
File:
- `backend/app/agents/ingestion_agent.py`

The ingestion flow was updated so that the final SOW document uses `llm_metadata.normalized_response` as the primary extraction source when available.

This affects:
- obligations
- SLA terms
- vague clauses
- start date
- end date
- total value
- currency
- description

Fallback behavior remains in place if normalized metadata is unavailable.

Impact:
- the saved SOW document should better match the normalized Gemini output seen in debugging metadata
- frontend-rendered SOW content should be more consistent with LLM results

---

## 3. Made SOW document IDs unique per upload
Files:
- `backend/app/models/sow_models.py`
- `backend/app/agents/ingestion_agent.py`
- `backend/app/api/sow.py`

### Previous behavior
SOW IDs were generated from `sow_number` only.

### New behavior
A unique upload suffix is now included in the SOW `_id`.

Conceptually:

```python
SOW-{sow_number}-{upload_suffix}
```

The upload flow now:
- generates a unique `upload_id` in the upload API
- passes that `upload_id` through the ingestion agent
- uses it when creating the SOW document

Impact:
- every upload creates a new Firestore document
- older uploads are preserved
- repeated use of the same `sow_number` no longer overwrites an existing SOW

---

## 4. Prevented Firestore record replacement on repeated uploads
Files:
- `backend/app/models/sow_models.py`
- `backend/app/api/sow.py`

Because `_id` is now unique per upload, `_save_sow_document()` no longer collides with older SOW records for repeated uploads.

Impact:
- Firestore keeps historical uploaded SOWs instead of replacing them
- the UI can show separate SOW entries rather than reflecting a previously overwritten one

---

## 5. Improved dynamic action generation upstream
Files:
- `backend/app/api/sow.py`
- `backend/app/agents/ingestion_agent.py`
- `backend/app/agents/monitoring_agent.py`

Improvements include:
- obligation risk scoring based on deadline urgency, penalties, complexity, and dependency signals
- vague clause severity based on clause content instead of defaulting too often
- scope-creep detection no longer always injecting a constant demo item
- action creation using more conditional logic from actual runtime signals

Impact:
- different SOWs should produce more varied review/action outputs
- the system is less likely to generate identical action patterns for unrelated uploads

---

## 6. Router/API alignment already addressed in this workstream
File:
- `backend/app/main_demo.py`

The SOW router was mounted with the correct prefix:
- `/api/v1/sow`

This allows the frontend dashboard and upload calls to reach the expected endpoints.

---

## Files Changed in This Context

### Core parsing and metadata
- `backend/app/agents/ingestion_agent.py`

### Transformation / Gemini setup
- `backend/app/agents/transformation_agent.py`

### Scope creep and monitoring behavior
- `backend/app/agents/monitoring_agent.py`

### Upload API and SOW response handling
- `backend/app/api/sow.py`

### Config support for Gemini API key
- `backend/app/core/config.py`

### App router mounting
- `backend/app/main_demo.py`

### SOW ID generation / document model
- `backend/app/models/sow_models.py`

---

## Commits on This Branch

- `c575ac5` — Improve SOW parsing metadata and UI sync
- `247eeec` — Prevent SOW upload overwrites in Firestore

---

## Validation Checklist

After restarting the backend, validate the following:

### Upload behavior
- upload one SOW
- upload a second different SOW
- upload another SOW with the same `sow_number`
- confirm each upload creates a separate SOW record

### API validation
Check:
- `POST /api/v1/sow/upload`
- `GET /api/v1/sow/list`
- `GET /api/v1/sow/dashboard/summary`

Confirm:
- unique `_id` values are returned for each uploaded SOW
- older SOWs are still present
- list ordering reflects the newest upload by `updated_at` / `created_at`

### Metadata validation
Inspect upload responses and confirm:
- `llm_metadata.response_preview` changes appropriately across different SOWs
- `llm_metadata.parsed_response` reflects the model output
- `llm_metadata.normalized_response` matches the persisted SOW content more closely

### UI validation
Confirm:
- the latest upload appears as a separate SOW in the UI
- previous uploads are not replaced
- the UI reflects the correct parsed content for each upload

---

## Restart Instructions

Backend restart recommended after these changes:

```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main_demo:app --host 0.0.0.0 --port 8000
```

If port 8000 is already occupied, stop the old process first.

---

## Known Notes

### 1. Existing overwritten records cannot be automatically restored
If an older SOW was already overwritten before this fix, that previous state is not recoverable unless it exists elsewhere.

### 2. IDE/type-check warnings were observed
Editor warnings were reported for imports such as:
- `fastapi`
- `docx`
- `pdfplumber`
- `google.genai`
- IBM SDK imports

These appear to be environment/type-resolution issues and are separate from the functional fixes documented here.

### 3. Repository push initially failed due to permissions
Pushes originally failed because GitHub authenticated as a user without write access. That was later resolved, and the feature branch was pushed successfully.

---

## Outcome

This PR improves the reliability of the SOW upload flow by ensuring:
- Gemini output is observable and debuggable
- persisted SOW data better matches normalized LLM output
- uploads no longer overwrite previous Firestore records
- the UI can display newly uploaded SOWs as distinct entries
- action generation is more dynamic and less demo-like