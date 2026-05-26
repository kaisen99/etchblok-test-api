---
{title: Architecture Overview, description: Architecture diagrams and documentation for etchblok-test-api, displayed_sidebar: architectureSidebar, section_type: architecture}
---
# Architecture Overview

This section contains architecture diagrams and documentation for **etchblok-test-api**.

## Available Diagrams

### [Bookmark Management System Context](/architecture/architecture-overview/bookmark-management-system-context)

This system context diagram depicts the [Bookmark API Internal Component Architecture](/architecture/architecture-overview/bookmark-api-internal-component-architecture) as the central system managing bookmark data. It interacts with an End User who consumes the REST API to perform CRUD operations on bookmarks, tags, and collections. The system relies on three primary external-facing components (currently implemented as in-memory stubs or internal services): a [Data Persistence](/guides/data-persistence) for persistent storage of domain entities, an [Search Architecture](/guides/search-indexing/search-architecture) for full-text indexing and retrieval, and a [Service Architecture and Caching](/guides/bookmark-services/service-architecture-and-caching) to optimize performance for frequently accessed resources.

The architecture follows a clean separation of concerns, where the API layer delegates business logic to a service layer, which in turn orchestrates interactions with the repository (database), search index, and cache. While the current implementation uses in-memory versions of these dependencies, the codebase includes configuration and connection stubs (e.g., for PostgreSQL) to facilitate future integration with real external systems.

**Key Architectural Findings:**
- The system is a Flask-based REST API providing endpoints for bookmarks, tags, and collections management.
- A service layer (BookmarkService) acts as a facade, orchestrating logic between the API routes and the data/search layers.
- Data persistence is abstracted through a repository pattern, currently using an in-memory store but designed for a PostgreSQL-like database.
- Full-text search is provided by an inverted index (SearchIndex) that tokenizes bookmark titles and descriptions.
- Performance is enhanced by an internal LRU cache that stores recently accessed bookmark objects.
- Internal health and diagnostic endpoints are provided for monitoring and readiness checks.

### [Bookmark API Internal Component Architecture](/architecture/architecture-overview/bookmark-api-internal-component-architecture)

The internal architecture of the Bookmark API follows a classic layered pattern, centered around a service-oriented design. 

At the core is the [app.services.bookmark_service](/api_ref/app/bookmark_service), which acts as a facade and orchestrator for all business logic. It is implemented as a singleton to ensure consistent state across the application's Flask blueprints. This service coordinates between the [app.db.repository](/api_ref/app/repository) for data persistence, the [app.services.search_service](/api_ref/app/search_service) for full-text indexing, and an internal app.services._cache for performance optimization.

The [app.db.repository](/api_ref/app/repository) provides an abstraction over the data storage, currently implemented as an in-memory store for [Bookmark Model](/api_ref/app/models/bookmark/bookmark) and other domain entities. The [app.services.search_service](/api_ref/app/search_service) maintains an inverted index of bookmark titles and descriptions, allowing for efficient keyword searches.

The [app.config](/api_ref/app/config) module provides environment-specific settings that configure the Flask application and its various components. The API layer, composed of several Flask blueprints, delegates all complex operations to the service layer, ensuring a clean separation of concerns.

**Key Architectural Findings:**
- BookmarkService is a singleton facade that orchestrates business logic, validation, and cross-component coordination.
- The system uses an in-memory BookmarkRepository for data persistence, abstracting the storage implementation from the service layer.
- A custom SearchIndex provides full-text search capabilities by tokenizing bookmark content and maintaining an inverted index.
- An internal LRUCache is used by the BookmarkService to speed up frequent bookmark lookups and is automatically invalidated on updates.
- The application follows a strict layered architecture: Routes (API) -> Services (Logic) -> Repository/Search/Cache (Data).

### [Bookmark Domain Entity Relationship Diagram](/architecture/architecture-overview/bookmark-domain-entity-relationship-diagram)

The data model for the Pagemark API centers around three core domain entities: [Bookmark](/api_ref/app/models/bookmark/bookmark), [Collection](/api_ref/app/models/collection/collection), and [Tag](/api_ref/app/models/tag/tag). 

- **Bookmark**: The primary entity, representing a saved URL with metadata. It maintains a many-to-many relationship with **Tags** via a list of tag IDs. It also tracks its lifecycle state through a `status` field (Active, Archived, or Trashed).
- **Tag**: A label used to organize bookmarks. It includes a `usage_count` to track how many bookmarks it is attached to and a `color` for UI categorization.
- **Collection**: A grouping mechanism for bookmarks. Collections can be **Manual** (explicitly added bookmarks) or **Smart** (automatically populated based on a `filter_rule`). It maintains a many-to-many relationship with **Bookmarks**.
- **User**: While not explicitly defined as a model class in the current implementation, it is a key logical entity mentioned in domain requirements (e.g., tags being unique per user).

The relationships are implemented using ID references in the model classes, reflecting the in-memory repository's structure where entities are stored in dictionaries and linked by their unique identifiers.

**Key Architectural Findings:**
- The system uses Python dataclasses for domain models (Bookmark, Collection, Tag).
- Relationships are managed via lists of IDs (e.g., Bookmark.tags, Collection.bookmark_ids) rather than ORM-style object references.
- Enums are used to define fixed states for BookmarkStatus, CollectionType, and TagColor.
- A User entity is implied by domain constraints (e.g., Tag uniqueness) but is not yet explicitly modeled in the persistence layer.
- Smart Collections use a filter_rule string to dynamically select bookmarks, while Manual Collections store a static list of IDs.

### [Bookmark Entity Lifecycle](/architecture/architecture-overview/bookmark-entity-lifecycle)

The state diagram illustrates the lifecycle of a [Bookmark](/api_ref/app/models/bookmark/bookmark) entity within the system. 

A bookmark begins its lifecycle in the **Active** state upon creation via the `create_bookmark` service method. From there, it can transition between three primary states: **Active**, **Archived**, and **Trashed**.

- **Active**: The default state where the bookmark is fully visible and searchable.
- **Archived**: A state for bookmarks that are no longer active but kept for reference. This is triggered by the `archive_bookmark` method.
- **Trashed**: A soft-deleted state. Bookmarks are moved here via the `delete_bookmark` method instead of being immediately removed from the database.

Key characteristics of these transitions include:
- **Restoration**: Bookmarks in either the **Archived** or **Trashed** states can be returned to the **Active** state using the `restore_bookmark` method.
- **Inter-state movement**: The system allows moving a bookmark directly from **Trashed** to **Archived** and vice versa, providing flexibility in how users manage their saved content.
- **Metadata Updates**: The `update_bookmark` method allows modifying fields like title and URL without changing the bookmark's status. Every state transition (including updates) triggers an internal `_touch()` call that refreshes the `updated_at` timestamp.
- **Persistence**: All state changes are persisted via the `BookmarkRepository`, and the internal cache is invalidated to ensure consistency across the service.

**Key Architectural Findings:**
- The Bookmark entity uses a BookmarkStatus enum with three values: ACTIVE, ARCHIVED, and TRASHED.
- The delete_bookmark service method performs a soft-delete by transitioning the bookmark to the TRASHED state rather than removing it from the repository.
- The restore_bookmark method is a unified way to move bookmarks from both ARCHIVED and TRASHED states back to ACTIVE.
- Every state transition calls a private _touch() method to update the modification timestamp (updated_at).
- The repository contains a hard-delete method (delete_bookmark), but it is not currently exposed through the BookmarkService or the REST API.
