---
{title: Architecture Overview, description: Architecture diagrams and documentation for etchblok-test-api, displayed_sidebar: architectureSidebar, section_type: architecture}
---
# Architecture Overview

This section contains architecture diagrams and documentation for **etchblok-test-api**.

## Available Diagrams

### [Bookmark Management System Context](/architecture/architecture-overview/bookmark-management-system-context)

This system context diagram depicts the **Bookmark Management System** (Bookmark API) and its interactions with external actors and dependencies. 

The central component is the **Bookmark API**, a Flask-based RESTful service that provides endpoints for managing bookmarks, tags, and collections. 

- **User**: Represents the end-users who interact with the system via the REST API to perform CRUD operations on their bookmarks.
- **Database**: A PostgreSQL database (as indicated by the internal connection configuration) used for persistent storage of domain entities like bookmarks, tags, and collections.
- **External Search Service**: A full-text search engine (such as Elasticsearch or Typesense) that the API uses to index bookmark content and provide advanced search capabilities. While currently implemented as an in-memory index, the architecture is designed for external integration.
- **Cache Service**: A caching layer (like Redis) used to store frequently accessed bookmark data to reduce database load and improve response times. The codebase includes an LRU cache implementation as a placeholder for this service.

The diagram shows the flow of data and requests between these components, highlighting the system's role as an orchestrator between user requests and backend storage/search services.

**Key Architectural Findings:**
- The Bookmark API is a Flask-based service providing RESTful endpoints for bookmark management.
- Data persistence is architected for a PostgreSQL database, with connection settings pointing to port 5432.
- Full-text search is decoupled into a dedicated service, with the codebase providing an in-memory implementation that is production-ready for Elasticsearch or Typesense.
- A caching layer (LRU cache) is integrated into the service layer to optimize bookmark retrieval.
- The system follows a layered architecture (Routes -> Services -> Repository/Search/Cache) to maintain separation of concerns.

### [Bookmark API Component Architecture](/architecture/architecture-overview/bookmark-api-component-architecture)

The component architecture of the Bookmark API follows a classic layered pattern, with a clear separation between the web interface, business logic, and data persistence.

At the top level, the [Bookmark API Component Architecture](/architecture/architecture-overview/bookmark-api-component-architecture) consists of Flask Blueprints that handle HTTP requests and responses. These routes do not contain business logic; instead, they delegate all operations to the [Bookmark Service API Reference](/api_ref/app/bookmark_service).

The [Bookmark Service API Reference](/api_ref/app/bookmark_service) is centered around the `BookmarkService`, which acts as a singleton facade. It orchestrates three main sub-components:
1.  **Search Service**: An in-memory inverted index that provides full-text search capabilities.
2.  **Cache Service**: An internal LRU cache used to optimize frequent lookups of individual bookmarks.
3.  **Bookmark Repository**: The data access layer that abstracts the underlying storage.

The [Persistence Layer](/guides/persistence-layer) currently implements an in-memory repository, which manages the lifecycle of the [Domain Models Guide](/guides/domain-models) (Bookmarks, Tags, and Collections). This design allows for easy replacement with a persistent database (like PostgreSQL or SQLite) without modifying the service or route logic.

Key architectural decisions discovered:
- **Singleton Service**: `BookmarkService` ensures a single point of truth for state management across different route modules.
- **Internal Caching**: The cache is encapsulated within the service layer, ensuring that invalidation happens automatically during write operations.
- **In-memory Search**: The search index is rebuilt from the repository on startup and updated incrementally, providing fast search without external dependencies.

**Key Architectural Findings:**
- The application implements a strict layered architecture: Routes -> Services -> Repository.
- BookmarkService is a singleton facade that orchestrates business logic, validation, and cross-component coordination.
- SearchIndex provides full-text search by maintaining an inverted index of bookmark titles and descriptions.
- LRUCache is used internally by the service layer to minimize repository hits for single-entity lookups.
- The BookmarkRepository provides a clean abstraction for data access, currently backed by in-memory dictionaries.

### [Bookmark Domain Data Model](/architecture/architecture-overview/bookmark-domain-data-model)

The data model for the Pagemark API is centered around three primary domain entities: [Bookmark Model](/api_ref/app/models/bookmark/bookmark), [Tag Model](/api_ref/app/models/tag/tag), and [Collection Model](/api_ref/app/models/collection/collection). 

- **Bookmark**: The core entity representing a saved URL. It contains metadata such as title, description, and status (Active, Archived, Trashed). It maintains a list of associated tag IDs.
- **Tag**: A label used to organize bookmarks. Each tag has a name, a color, and a usage count that tracks how many bookmarks are currently using it.
- **Collection**: A grouping mechanism for bookmarks. Collections can be **manual** (where users explicitly add bookmarks) or **smart** (where bookmarks are automatically included based on a `filter_rule`).

The relationships are many-to-many:
- A **Bookmark** can have multiple **Tags**, and a **Tag** can be applied to multiple **Bookmarks**. This is implemented via a list of tag IDs within the Bookmark entity.
- A **Collection** can contain multiple **Bookmarks**, and a **Bookmark** can belong to multiple **Collections**. This is implemented via a list of bookmark IDs within the Collection entity.

Note: Although "User" was identified as a key entity in the system classification, the current codebase implements an in-memory repository that does not yet include a formal `User` model or multi-tenant support. References to "users" in the code comments suggest future intent for per-user uniqueness constraints.

**Key Architectural Findings:**
- The system uses a flat, in-memory data model with entities defined as Python dataclasses.
- Relationships (Bookmark-Tag and Collection-Bookmark) are managed using lists of identifiers rather than formal ORM relationship objects.
- Enums are used extensively to define states: BookmarkStatus (ACTIVE, ARCHIVED, TRASHED), TagColor (RED, BLUE, etc.), and CollectionType (MANUAL, SMART).
- Smart Collections use a 'filter_rule' string to dynamically select bookmarks based on title or description matches.
- The 'User' entity is mentioned in documentation and comments but is not yet implemented as a class or database field.

### [Bookmark Lifecycle States](/architecture/architecture-overview/bookmark-lifecycle-states)

The state diagram illustrates the lifecycle of a [Bookmark Model](/api_ref/app/models/bookmark/bookmark) entity within the system. 

### States
- **Active**: The default state for a newly created bookmark. These bookmarks are typically visible in the user's primary list.
- **Archived**: A state for bookmarks that the user wants to keep but remove from the active view.
- **Trashed**: A soft-deleted state. Bookmarks in this state are hidden from normal views but can still be restored.

### Transitions
- **Creation**: A bookmark enters the **Active** state upon creation via the `create_bookmark` service method.
- **Archiving**: A bookmark can be moved to the **Archived** state from either the **Active** or **Trashed** states using the `archive_bookmark` endpoint.
- **Trashing**: A bookmark is moved to the **Trashed** state via the `delete_bookmark` endpoint (which performs a soft-delete). This can happen from either the **Active** or **Archived** states.
- **Restoration**: A bookmark in the **Archived** or **Trashed** state can be returned to the **Active** state using the `restore_bookmark` endpoint.

The architecture uses a soft-delete pattern where the `TRASHED` status acts as a safety net before any potential (though currently unimplemented in the API) hard deletion. All state transitions are handled by the `BookmarkService` which updates the `status` field on the `Bookmark` model and persists the change via the `BookmarkRepository`.

**Key Architectural Findings:**
- The Bookmark entity has three primary states: ACTIVE, ARCHIVED, and TRASHED, defined in the BookmarkStatus enum.
- New bookmarks are initialized to the ACTIVE state by default.
- The API's DELETE method performs a soft-delete by transitioning the bookmark to the TRASHED state rather than removing it from the database.
- Transitions between states are fluid; for example, a bookmark can move directly from TRASHED to ARCHIVED or vice versa.
- The BookmarkRepository contains a hard-delete method (delete_bookmark), but it is not currently exposed through the BookmarkService or the REST API.
