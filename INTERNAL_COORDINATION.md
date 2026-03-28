# 📋 Internal Coordination of Requests

## Overview

The **Internal Coordination** feature allows request creators to track and mark their requests as **resolved/done**. This provides visibility into which requests have been successfully addressed by the community.

## Features

### 1. **Request Resolution Tracking**

- **Creator Status**: Request creators can mark their request as **done** after they have received adequate help or the request is resolved
- **Visual Indicators**:
  - ✅ **Hotovo (Done)** - Request creator has marked it as resolved
  - ⏳ **Čakajúce (Pending)** - Request is still awaiting creator confirmation

### 2. **Creator-Only Actions**

- Only the person who submitted the request can mark it as done
- The "Mark as Done" button is only visible to request creators
- Authentication is enforced on the backend

### 3. **Tracking Fields**

The Request model tracks:

- `is_resolved_by_creator` (Boolean): Whether the creator marked the request as done
- `creator_resolved_at` (DateTime): Timestamp when the creator marked it done

## How It Works

### For Request Creators

1. **View Your Requests**
   - Go to the "📋 Žiadosti" (Requests) tab in the dashboard
   - All requests with their current status are displayed

2. **Mark Request as Done**
   - Once your issue is resolved, click the **✅ Hotovo** (Done) button
   - The request status immediately updates to show as completed
   - A timestamp is recorded for reference

3. **See Resolution Status**
   - Each request shows a resolution status badge
   - Green "✅ Hotovo" badge for completed requests
   - Orange "⏳ Čakajúce" badge for pending requests

### For Administrative Tracking

- Admins can see which requests have been closed by creators
- Dashboard metrics can distinguish between:
  - Requests completed by creators (`is_resolved_by_creator=True`)
  - Requests still awaiting follow-up (`is_resolved_by_creator=False`)

## API Endpoints

### Mark Request as Done (Creator)

**POST** `/api/requests/{request_id}/mark_done_by_creator/`

```bash
curl -X POST http://localhost:8000/api/requests/123/mark_done_by_creator/
```

**Response:**

```json
{
  "status": "success",
  "message": "Request marked as done by creator",
  "is_resolved_by_creator": true,
  "creator_resolved_at": "2026-03-28T14:30:45Z"
}
```

**Permissions:**

- Only the request creator (user who submitted it) can call this endpoint
- Returns 403 Forbidden if unauthorized

## Database Schema

### Changes to Request Model

```python
# Request model additions:
is_resolved_by_creator = BooleanField(
    default=False,
    help_text='Whether the request creator has marked this as resolved/done'
)

creator_resolved_at = DateTimeField(
    null=True,
    blank=True,
    help_text='Timestamp when creator marked the request as done'
)
```

### Migration

- Migration: `0006_request_creator_resolved_at_and_more.py`
- Adds two new columns to the `server_request` table

## Frontend Components

### Updated Components

1. **RequestList Component** (`client/src/components/RequestList.jsx`)
   - New column for "Stav vyriešenia" (Resolution Status)
   - Shows resolution badges (Done/Pending)
   - Conditional "Mark Done" button for creators

2. **App Component** (`client/src/components/App.jsx`)
   - New `handleMarkDone()` function to call API
   - New `isCreator()` function to check if user is creator
   - Passes these handlers to RequestList

3. **Styling** (`client/src/App.css`)
   - `.badge.resolution-done` - Green badge for completed requests
   - `.badge.resolution-pending` - Orange badge for pending requests

## Usage Example

### In Dashboard

```
Request Title: "Help with Django deployment"
Status: In Progress
Resolution Status: ⏳ Čakajúce (Pending)
[🎯 Match] [✅ Hotovo]  <- Creator sees both buttons
```

After clicking "✅ Hotovo":

```
Request Title: "Help with Django deployment"
Status: In Progress
Resolution Status: ✅ Hotovo (Done)
[🎯 Match]  <- Only Match button visible now
```

## Admin View

In the admin panel, you can see:

- All requests with their creator resolution status
- Filter by `is_resolved_by_creator` to see completed vs pending requests
- View the `creator_resolved_at` timestamp for completed requests

## Future Enhancements

Possible extensions to this feature:

1. **Feedback Collection** (Not implemented per requirements)
   - Could add optional feedback/comments when marking as done
   - Would not be a mandatory quiz

2. **Resolution Metrics**
   - Dashboard widget showing % of requests marked done
   - Average time to resolution by category

3. **Notifications**
   - Notify admins when a creator marks request as done
   - Email confirmation to creator

4. **Follow-up Mechanism**
   - Allow creator to re-open a request if needed
   - Track multiple resolution/reopening cycles

## Notes

- This feature does NOT implement feedback quizzes (as per requirements)
- Resolution by creator is independent from administrative "resolved" status
- Both tracking mechanisms work in parallel for complete visibility
