---
{title: Architecture Overview, description: Architecture diagrams and documentation for etchblok-test-api, displayed_sidebar: architectureSidebar, section_type: architecture}
---
# Architecture Overview

This section contains architecture diagrams and documentation for **etchblok-test-api**.

## Available Diagrams

### [Bookmark Management System Context](/architecture/architecture-overview/bookmark-management-system-context)

The Bookmark Management System Context diagram illustrates the high-level interactions between the **Bookmark API** and its external environment. 

The **Bookmark API** is a Flask-based REST service that provides endpoints for managing bookmarks, tags, and collections. It serves as the central hub for business logic, orchestrating data between the user and various storage and utility services.

Key interactions include:
- **End Users** interact with the system via a RESTful API to perform CRUD operations on bookmarks, organize them into collections, and apply tags.
- The **Database** (represented in the code by a PostgreSQL connection stub) is used for persistent storage of domain entities like bookmarks, tags, and collections.
- An **External Search Service** (implemented as an in-memory inverted index in the current codebase) provides full-text search capabilities across bookmark titles and descriptions.
- A **Cache Service** (implemented as an in-memory LRU cache) is used to store frequently accessed bookmarks, reducing the load on the primary database and improving response times for read operations.

While the current implementation uses in-memory stubs for the database, search, and cache components, the architecture is designed to integrate with external systems like PostgreSQL, Elasticsearch, and Redis in a production environment. [BookmarkService](/api_ref/app/services/bookmark/service/bookmarkservice) acts as a facade that abstracts these integrations from the route handlers.

**Key Architectural Findings:**
- The system is a Flask-based REST API following a layered architecture (Routes, Services, Repository, Models).
- Persistence is managed through a repository pattern, with stubs for a PostgreSQL database connection pool.
- Full-text search is provided by a dedicated SearchIndex service that maintains an inverted index of bookmark content.
- Performance is optimized using an LRU (Least Recently Used) cache for bookmark lookups.
- The API includes internal health and readiness probes intended for use by load balancers and monitoring systems.

### [Bookmark API Component Architecture](/architecture/architecture-overview/bookmark-api-component-architecture)

The Bookmark API follows a classic layered architecture, where each layer has a distinct responsibility. 

The **Presentation Layer** consists of Flask Blueprints (like `app.routes.bookmarks`) that handle incoming HTTP requests and return JSON responses. These routes do not contain business logic; instead, they delegate all operations to the **Service Layer**.

The **Service Layer** is centered around the `BookmarkService`, which acts as a facade. It orchestrates complex operations, such as creating a bookmark, which involves validation, persisting to the repository, updating the search index, and invalidating the cache. The `SearchIndex` provides full-text search capabilities using an inverted index, while the `LRUCache` improves performance for frequent lookups.

The **Data Access Layer** is represented by the `BookmarkRepository`, which provides an abstraction over the data store. In this implementation, it manages in-memory collections of domain entities.

The **Domain Layer** contains the core data models (`Bookmark`, `Tag`, `Collection`) which are used throughout the application to pass data between layers.

Key design patterns discovered include the **Singleton** pattern for the `BookmarkService` to ensure shared state across the application, and the **Repository** pattern to decouple business logic from data storage details.

**Key Architectural Findings:**
- The `BookmarkService` acts as a central facade and singleton, orchestrating interactions between the repository, search index, and cache.
- The `SearchIndex` maintains an inverted index in memory, rebuilding it from the `BookmarkRepository` on initialization.
- An internal `LRUCache` is used by the service layer to optimize bookmark retrieval by ID.
- The `BookmarkRepository` provides a clean abstraction for CRUD operations, currently implemented as an in-memory store.
- Domain models like `Bookmark` are implemented as dataclasses with self-contained logic for state transitions (e.g., archive, trash).

### [Bookmark Domain Data Model](/architecture/architecture-overview/bookmark-domain-data-model)

The data model for the Bookmark Management API is centered around three primary domain entities: [Bookmark](/api_ref/app/models/bookmark/bookmark), [Collection](/api_ref/app/models/collection/collection), and [Tag](/api_ref/app/models/tag/tag). These entities are implemented as Python dataclasses and managed via an in-memory repository.

### Key Entities

- **Bookmark**: The core entity representing a saved URL. It includes metadata like title, description, and a status (Active, Archived, or Trashed). It also supports an extensible `metadata` dictionary for additional properties.
- **Tag**: A label that can be applied to bookmarks for organization. Each tag has a name, a color (from a fixed set of [TagColor](/api_ref/app/models/tag/tagcolor) values), and tracks its own `usage_count`.
- **Collection**: A grouping mechanism for bookmarks. Collections can be **Manual** (where bookmarks are added explicitly) or **Smart** (where bookmarks are automatically included based on a `filter_rule` that matches titles or descriptions).

### Relationships

- **Bookmark <-> Tag**: A many-to-many relationship. A bookmark can have multiple tags, and a tag can be associated with many bookmarks. This is implemented via a list of tag IDs stored on the `Bookmark` entity.
- **Collection <-> Bookmark**: A many-to-many relationship. A collection contains a list of bookmark IDs. While a bookmark typically belongs to one or more collections, the relationship is managed by the `Collection` entity. Smart collections dynamically resolve their member bookmarks at runtime based on their filter rules.

### Enumerations

The model uses several enumerations to define fixed states:
- `BookmarkStatus`: `ACTIVE`, `ARCHIVED`, `TRASHED`
- `CollectionType`: `MANUAL`, `SMART`
- `TagColor`: `RED`, `BLUE`, `GREEN`, `YELLOW`, `PURPLE`, `GRAY`

**Key Architectural Findings:**
- Entities are implemented as Python dataclasses with UUID-based string primary keys of varying lengths (12 chars for Bookmarks, 10 for Collections, 8 for Tags).
- Relationships are managed through ID lists (e.g., Bookmark.tags, Collection.bookmark_ids) rather than traditional ORM back-references, reflecting the in-memory repository architecture.
- The system supports 'Smart Collections' which use a filter_rule string to dynamically group bookmarks based on text matching in titles and descriptions.
- Bookmarks include a flexible metadata dictionary for extensibility beyond the core fields.
- Tags maintain a usage_count which is incremented/decremented by the service layer when tags are attached or removed.

### [Bookmark Entity Lifecycle](/architecture/architecture-overview/bookmark-entity-lifecycle)

The state machine for the [Bookmark](/api_ref/app/models/bookmark/bookmark) entity is managed through the `BookmarkStatus` enum. It follows a simple lifecycle where bookmarks are created in an **Active** state and can be moved to **Archived** or **Trashed** (soft-deleted) states. 

The system uses a layered approach where the [BookmarkService](/api_ref/app/services/bookmark/service/bookmarkservice) orchestrates these transitions by calling domain methods on the `Bookmark` model and then persisting the changes via the [BookmarkRepository](/api_ref/app/db/repository/bookmarkrepository). 

Key characteristics of this lifecycle include:
- **Soft Deletion**: The `delete_bookmark` operation does not remove the record from the database but instead transitions it to the `TRASHED` state.
- **Bidirectional Transitions**: The model allows moving between any of the three states (Active, Archived, Trashed) without restrictive guard conditions, provided the bookmark exists.
- **Persistence**: Every state transition triggers a `_touch()` call to update the `updated_at` timestamp and is immediately saved to the repository.

**Key Architectural Findings:**
- Bookmarks have three primary states: ACTIVE, ARCHIVED, and TRASHED, defined in the BookmarkStatus enum.
- The initial state for any new bookmark is ACTIVE, set during instantiation in the Bookmark dataclass.
- Transitions are triggered by specific API endpoints: DELETE /\<id> (trash), POST /\<id>/archive, and POST /\<id>/restore.
- The delete_bookmark service method implements a 'soft-delete' pattern by moving the entity to the TRASHED state rather than removing it.
- The domain model (Bookmark class) provides explicit methods (archive, trash, restore) to handle these state changes and update the modification timestamp.