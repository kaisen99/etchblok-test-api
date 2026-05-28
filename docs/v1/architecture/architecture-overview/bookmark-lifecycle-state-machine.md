---
{title: Bookmark Lifecycle State Machine, description: 'This state diagram illustrates the lifecycle of the two primary entities in the Etchblok API: and . The Bookmark Lifecycle is governed by the BookmarkStatus...', displayed_sidebar: architectureSidebar, section_type: architecture}
---
# Bookmark Lifecycle State Machine

This state diagram illustrates the lifecycle of the two primary entities in the Etchblok API: [The Bookmark Entity](/guides/domain-models/the-bookmark-entity) and [Understanding Collections](/guides/categorization-collections/understanding-collections).

The **Bookmark Lifecycle** is governed by the `BookmarkStatus` enum. Every bookmark begins in the `ACTIVE` state upon creation. From there, it can be moved to `ARCHIVED` (for long-term storage) or `TRASHED` (a soft-delete state). The system allows for fluid transitions between these states: a trashed item can be restored to active or moved directly to the archive, and an archived item can be trashed or restored. All state transitions trigger a "touch" operation that updates the `updated_at` timestamp.

The **Collection Lifecycle** is defined by the `CollectionType` (Manual vs. Smart) and a pinning mechanism. 
- **Manual Collections** are user-managed lists where bookmarks are explicitly added or removed.
- **Smart Collections** are dynamic and populate themselves based on a `filter_rule` (e.g., matching keywords in titles or descriptions).
- Both types support a **Pinned** state (via the `is_pinned` flag), which determines their visibility in the UI sidebar, although the current REST API implementation primarily focuses on the creation and membership management of these collections.

Key architectural decisions discovered include the use of **soft-deletion** for bookmarks (moving them to `TRASHED` rather than immediate removal) and the **singleton service pattern** (`BookmarkService`) which orchestrates these state changes across the repository and search index.

**Key Architectural Findings:**
- Bookmarks use a three-state lifecycle: ACTIVE, ARCHIVED, and TRASHED.
- The 'delete' operation in the BookmarkService is a soft-delete that transitions the entity to the TRASHED state.
- Restoration (restore_bookmark) always returns a bookmark to the ACTIVE state, regardless of whether it was archived or trashed.
- Collections are categorized into MANUAL and SMART types at creation, which dictates how their membership is managed.
- A pinning mechanism (is_pinned) exists in the Collection model to manage UI priority, though it is not yet exposed via the public REST routes.
- Every state transition in the Bookmark model calls an internal _touch() method to maintain auditability via updated_at timestamps.

```mermaid
stateDiagram-v2
    state "Bookmark Lifecycle" as Bookmark {
        [*] --> ACTIVE: "create_bookmark()"
        
        ACTIVE --> ARCHIVED: "archive_bookmark()"
        ACTIVE --> TRASHED: "delete_bookmark()"
        
        ARCHIVED --> ACTIVE: "restore_bookmark()"
        ARCHIVED --> TRASHED: "delete_bookmark()"
        
        TRASHED --> ACTIVE: "restore_bookmark()"
        TRASHED --> ARCHIVED: "archive_bookmark()"

        note right of ACTIVE
            Visible in main feed.
            Default state.
        end note

        note right of TRASHED
            Soft-deleted.
            Excluded from search.
        end note
    }

    state "Collection Lifecycle" as Collection {
        [*] --> MANUAL: "create(type=#quot;manual#quot;)"
        [*] --> SMART: "create(type=#quot;smart#quot;)"

        state MANUAL {
            [*] --> Unpinned_M
            Unpinned_M --> Pinned_M: "pin()"
            Pinned_M --> Unpinned_M: "unpin()"
            
            state "Membership" as Mem {
                [*] --> Empty
                Empty --> Populated: "add_bookmark()"
                Populated --> Empty: "remove_bookmark()"
            }
        }

        state SMART {
            [*] --> Unpinned_S
            Unpinned_S --> Pinned_S: "pin()"
            Pinned_S --> Unpinned_S: "unpin()"
            
            state "Dynamic Filter" as Filter {
                [*] --> Evaluating: "_apply_filter()"
                Evaluating --> Evaluating: refresh
            }
        }
    }
```
