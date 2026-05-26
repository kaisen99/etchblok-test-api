---
{title: Architecture Overview, description: Architecture diagrams and documentation for etchblok-test-api, displayed_sidebar: architectureSidebar, section_type: architecture}
---
# Architecture Overview

This section contains architecture diagrams and documentation for **etchblok-test-api**.

## Available Diagrams

### [Bookmark Management System Context](/architecture/architecture-overview/bookmark-management-system-context)

This system context diagram illustrates the **Pagemark API** as the central component of a bookmark management ecosystem. The API, built with [Flask API Layered Architecture](/architecture/architecture-overview/flask-api-layered-architecture), serves as the orchestration layer for managing bookmarks, tags, and collections.

The diagram highlights the following key interactions:
- **User**: End-users or client applications interact with the system via a RESTful HTTP API to perform CRUD operations on bookmarks and organize them into collections.
- **Database**: A persistent storage layer (designed for PostgreSQL) where the API stores domain entities such as bookmarks, tags, and collection metadata.
- **External Search Service**: The API integrates with a search service (intended to be Typesense or Elasticsearch) to provide full-text search capabilities across bookmark titles and descriptions.
- **Cache Service**: An LRU-based caching layer (implemented in-memory but extensible to Redis) is used to optimize performance for frequently accessed bookmark data.

The architecture follows a clean separation of concerns, with a dedicated repository layer for data access and a service layer for business logic and external service orchestration.

**Key Architectural Findings:**
- The system is a Flask-based REST API with a layered architecture (Routes, Services, Repository, Models).
- A dedicated database connection module (`app/db/_connection.py`) defines a pool for a PostgreSQL-compatible database.
- The search functionality is abstracted into a `SearchIndex` service, designed to be backed by external full-text search engines.
- An internal LRU cache is used by the `BookmarkService` to reduce database load for read-heavy operations.
- The API includes internal health and readiness probes (`/_internal/health`) intended for use by load balancers and monitoring systems.

### [Flask API Layered Architecture](/architecture/architecture-overview/flask-api-layered-architecture)

The Flask API follows a classic layered architecture, with a clear separation between the web interface, business logic, and data access.

### API Layer
The [Flask API Layered Architecture](/architecture/architecture-overview/flask-api-layered-architecture) is implemented using Flask Blueprints (`bookmarks`, `tags`, `collections`). These blueprints define the RESTful endpoints and handle HTTP request/response cycles. They delegate all business logic to the `BookmarkService`.

### Service Layer
The [Service Layer](/guides/service-layer) contains the core business logic.
- **BookmarkService**: Acts as a facade and singleton orchestrator. It coordinates operations between the repository, the search index, and an internal LRU cache.
- **SearchService (SearchIndex)**: Provides in-memory full-text search capabilities. It maintains an inverted index of bookmark titles and descriptions and is updated incrementally by the `BookmarkService`.
- **LRUCache**: An internal component used by the `BookmarkService` to speed up retrieval of frequently accessed bookmarks.

### Data Access Layer
The [The Repository Architecture](/guides/data-persistence/the-repository-architecture) is centered around the `BookmarkRepository`.
- **BookmarkRepository**: Provides an abstraction over the storage mechanism. In this implementation, it manages an in-memory data store for bookmarks, tags, and collections. It is responsible for CRUD operations and basic filtering/pagination.
- **In-Memory Storage**: Serves as the "database" for the application, holding the state of all domain entities during the application's lifecycle.

### Domain Models
The [Core Entities](/guides/core-entities) (`Bookmark`, `Tag`, `Collection`) are plain Python objects (using `dataclasses`) that represent the core entities. They contain basic validation logic and serialization methods (`to_dict`, `from_dict`).

### Configuration
The application uses a class-based configuration system (`DevelopmentConfig`, `ProductionConfig`) to manage environment-specific settings like page sizes and cache TTLs.

**Key Architectural Findings:**
- The application uses a Singleton pattern for the `BookmarkService` to ensure shared state (cache and search index) across different Flask blueprints.
- The `SearchIndex` is an in-memory inverted index that rebuilds itself from the `BookmarkRepository` on initialization and receives incremental updates.
- The `BookmarkRepository` acts as both the data access layer and the storage engine, maintaining internal dictionaries for bookmarks, tags, and collections.
- A clear dependency flow exists from API Blueprints -> BookmarkService -> BookmarkRepository, adhering to the layered architecture principle.
- Domain models are decoupled from the storage implementation, allowing them to be used across all layers for data transfer and serialization.

### [Bookmark Domain Entity Relationship Diagram](/architecture/architecture-overview/bookmark-domain-entity-relationship-diagram)

The Bookmark Domain Entity Relationship Diagram illustrates the core data structures and their associations within the Etchblok API. 

### Core Entities
- **Bookmark**: The central entity representing a saved URL. It includes metadata like `title`, `description`, and `status` (Active, Archived, Trashed). It also tracks its own lifecycle via `created_at` and `updated_at` timestamps.
- **Tag**: A label used to categorize bookmarks. Each tag has a `name`, a `color` (from a predefined set of Enums), and a `usage_count` that tracks how many bookmarks it is attached to.
- **Collection**: A grouping mechanism for bookmarks. Collections can be **Manual** (where bookmarks are explicitly added) or **Smart** (where bookmarks are automatically included based on a `filter_rule`).

### Relationships
- **Bookmark-Tag Association**: A many-to-many relationship. In the code, this is implemented as a list of tag IDs within the `Bookmark` dataclass. The diagram represents this via the `BOOKMARK_TAG` association entity.
- **Collection-Bookmark Association**: A many-to-many relationship. A collection can contain multiple bookmarks, and a bookmark can belong to multiple collections. In the code, this is managed by the `bookmark_ids` list in the `Collection` dataclass.

### Implementation Details
The system uses an in-memory repository (`BookmarkRepository`) to manage these entities. While the current implementation uses Python dataclasses and lists for relationships, the diagram reflects the logical relational model that these structures represent. Enums like `BookmarkStatus`, `TagColor`, and `CollectionType` provide domain-specific constraints on the entity attributes.

**Key Architectural Findings:**
- The system uses Python dataclasses (Bookmark, Tag, Collection) to represent domain entities.
- Relationships are managed via lists of IDs (e.g., Bookmark.tags, Collection.bookmark_ids), representing many-to-many associations.
- Enums are used for entity states and types: BookmarkStatus (ACTIVE, ARCHIVED, TRASHED), TagColor (RED, BLUE, etc.), and CollectionType (MANUAL, SMART).
- The BookmarkRepository provides an in-memory abstraction for CRUD operations on these entities.
- Smart Collections use a 'filter_rule' string to dynamically select bookmarks based on title or description matches.

### [Bookmark Entity Lifecycle](/architecture/architecture-overview/bookmark-entity-lifecycle)

This state diagram depicts the lifecycle of the [The Bookmark Entity](/guides/core-entities/the-bookmark-entity) entity. A bookmark is initialized in the `ACTIVE` state upon creation. It can transition between three primary states: `ACTIVE`, `ARCHIVED`, and `TRASHED`. The `TRASHED` state acts as a soft-delete mechanism, allowing bookmarks to be recovered later. Transitions are managed by the `BookmarkService`, which ensures that the `updated_at` timestamp is refreshed (via the `_touch` method) whenever a state change occurs. While the repository layer supports hard deletion, the current service implementation focuses on these three managed states.

**Key Architectural Findings:**
- The `Bookmark` entity uses a `BookmarkStatus` enum with three values: `ACTIVE`, `ARCHIVED`, and `TRASHED`.
- New bookmarks are always created in the `ACTIVE` state by default.
- The `delete_bookmark` service method performs a soft-delete by transitioning the entity to the `TRASHED` state.
- The `restore_bookmark` method is used to return both `ARCHIVED` and `TRASHED` bookmarks to the `ACTIVE` state.
- Transitions are not restricted by the current state; for example, a `TRASHED` bookmark can be directly `ARCHIVED` and vice versa.
- Every state transition triggers a call to the internal `_touch()` method to update the modification timestamp.
