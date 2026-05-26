---
{title: Bookmark Entity Lifecycle, description: This state diagram depicts the lifecycle of the entity. A bookmark is initialized in the ACTIVE state upon creation. It can transition between three primary..., displayed_sidebar: architectureSidebar, section_type: architecture}
---
# Bookmark Entity Lifecycle

This state diagram depicts the lifecycle of the [The Bookmark Entity](/guides/core-entities/the-bookmark-entity) entity. A bookmark is initialized in the `ACTIVE` state upon creation. It can transition between three primary states: `ACTIVE`, `ARCHIVED`, and `TRASHED`. The `TRASHED` state acts as a soft-delete mechanism, allowing bookmarks to be recovered later. Transitions are managed by the `BookmarkService`, which ensures that the `updated_at` timestamp is refreshed (via the `_touch` method) whenever a state change occurs. While the repository layer supports hard deletion, the current service implementation focuses on these three managed states.

**Key Architectural Findings:**
- The `Bookmark` entity uses a `BookmarkStatus` enum with three values: `ACTIVE`, `ARCHIVED`, and `TRASHED`.
- New bookmarks are always created in the `ACTIVE` state by default.
- The `delete_bookmark` service method performs a soft-delete by transitioning the entity to the `TRASHED` state.
- The `restore_bookmark` method is used to return both `ARCHIVED` and `TRASHED` bookmarks to the `ACTIVE` state.
- Transitions are not restricted by the current state; for example, a `TRASHED` bookmark can be directly `ARCHIVED` and vice versa.
- Every state transition triggers a call to the internal `_touch()` method to update the modification timestamp.

```mermaid
stateDiagram-v2
    [*] --> Active: "create_bookmark()"
    
    Active --> Archived: "archive_bookmark()"
    Active --> Trashed: "delete_bookmark()"
    
    Archived --> Active: "restore_bookmark()"
    Archived --> Trashed: "delete_bookmark()"
    
    Trashed --> Active: "restore_bookmark()"
    Trashed --> Archived: "archive_bookmark()"
    
    Active --> Active: "update_bookmark()"
    Archived --> Archived: "update_bookmark()"
    Trashed --> Trashed: "update_bookmark()"

    note right of Active
        Initial state.
        Visible in default views.
    end note

    note right of Archived
        Long-term storage.
        Hidden from main list.
    end note

    note right of Trashed
        Soft-deleted.
        Can be restored or archived.
    end note
```
