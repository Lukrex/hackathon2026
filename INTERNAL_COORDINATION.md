# Internal Coordination

This file describes the internal operating workflow of the platform.

## Roles

### Request creator

- submits requests
- tracks request progress
- communicates in request chat
- confirms completion

### Expert

- maintains profile and availability
- handles assigned tasks
- can leave tasks if needed
- receives karma and help credit on confirmed completion

### Worker

- internal staff role (non-superuser)
- processes only assigned categories
- sees only scoped request subsets

### Super-admin

- sees all requests
- manages workers and categories
- assigns/unassigns experts
- can permanently delete requests

## Request lifecycle

1. User submits a request via form.
2. Request is stored as open.
3. Internal team reviews and prioritizes.
4. System suggests experts, or team assigns manually.
5. Communication continues in request and internal chats.
6. Request creator marks completion.
7. Expert credit and busy/free status are updated.

## Coordination advantages

Compared with a basic ticket list, this system adds:

- role-separated responsibility model
- explicit request-owner and expert linkage
- request-scoped chat context
- requester-verified completion
- karma and help history for experts

## Chat layers

The app supports multiple conversation channels:

- request chat (request-scoped)
- admin chat
- company chat
- direct chat between Tier 1 and Tier 2 accounts

Read-state and mute controls reduce communication noise.

## Worker management

Super-admins can assign category access to workers, allowing structured work distribution across domains such as hiring, investment, and marketing.

## Completion model

A request is considered truly completed when the creator confirms it. At that point the system records:

- `is_resolved_by_creator = True`
- `creator_resolved_at`
- `completed_by_expert`
- `resolved_at` (if not already set)

The selected expert also gets:

- `karma_points + 1`
- `help_provided + 1`
