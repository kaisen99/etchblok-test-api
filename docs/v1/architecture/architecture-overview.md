---
{title: Architecture Overview, description: Architecture diagrams and documentation for etchblok-test-api, displayed_sidebar: architectureSidebar, section_type: architecture}
---
# Architecture Overview

This section contains architecture diagrams and documentation for **etchblok-test-api**.

## Available Diagrams

### [System Context Diagram for Bookmark Management API](/architecture/architecture-overview/system-context-diagram-for-bookmark-management-api)

This system context diagram illustrates the architecture of the Bookmark Management API (Pagemark). The central Flask-based API orchestrates interactions between users and several external services. 

The API provides a RESTful interface for [System Context Diagram](/architecture/architecture-overview/system-context-diagram-for-bookmark-management-api) to manage bookmarks, tags, and collections. It relies on a [Data Persistence](/guides/data-persistence) (PostgreSQL) for persistent storage of domain entities. To optimize performance, it utilizes a [In-Memory Storage Architecture](/guides/data-persistence/in-memory-storage-architecture) (implemented as an LRU cache) for frequently accessed bookmark data. Full-text search capabilities are provided by an [Search Architecture](/guides/search-indexing/search-architecture) (such as Typesense or Elasticsearch), which the API keeps in sync by indexing bookmarks as they are created or updated. Additionally, the system exposes internal health and diagnostic endpoints for use by Monitoring Systems and load balancers.

**Key Architectural Findings:**
- The system is a Flask-based REST API following a layered architecture (Routes -> Services -> Repository).
- Data persistence is handled by a repository layer, which is designed to interface with a PostgreSQL database (stubbed in the current implementation).
- An internal LRU cache is used by the service layer to reduce database load for frequent bookmark lookups.
- Full-text search is implemented via a search index service, intended to be replaced by external services like Elasticsearch or Typesense in production.
- Internal health and readiness probes are provided for infrastructure monitoring and load balancing.

### [Component Architecture of the Bookmark API](/architecture/architecture-overview/component-architecture-of-the-bookmark-api)

The component architecture of the Bookmark API follows a layered approach, separating the external API interface from the core business logic and data persistence.

At the top, the **API Layer** consists of Flask Blueprints for [Core Entities Overview](/guides/domain-models/core-entities-overview), [Categorization with Tags](/guides/domain-models/categorization-with-tags), and [Organizing with Collections](/guides/domain-models/organizing-with-collections). These routes do not interact with the data layer directly; instead, they delegate all operations to the **BookmarkService**.

The **Service Layer** is centered around the `BookmarkService`, which acts as a singleton orchestrator. It manages the flow of data between the repository, the search index, and the cache.
- The **SearchService** (implemented as `SearchIndex`) maintains an in-memory inverted index for full-text search. It is rebuilt from the repository on startup and updated incrementally.
- The **Cache Manager** (implemented as `LRUCache`) stores recently accessed bookmarks to reduce repository lookups.

The **Data Layer** contains the `BookmarkRepository`, which provides an abstraction over the in-memory storage of domain entities.

Finally, the **Domain Models** (`Bookmark`, `Tag`, `Collection`) are shared across all layers, defining the structure and basic behavior of the system's core entities.

**Key Architectural Findings:**
- BookmarkService acts as a Singleton Facade, orchestrating all business logic and cross-entity operations.
- SearchService (SearchIndex) implements an in-memory inverted index that depends on the BookmarkRepository for initial data loading.
- Cache Manager (LRUCache) is integrated directly into the BookmarkService to provide transparent caching for bookmark retrieval.
- The architecture strictly separates the API routing (Flask Blueprints) from the service logic, ensuring that routes only depend on the BookmarkService.
- Data persistence is abstracted through the BookmarkRepository, which currently uses in-memory dictionaries but is designed for easy replacement with a database.

### [Domain Data Model for Bookmarks, Collections, and Tags](/architecture/architecture-overview/domain-data-model-for-bookmarks-collections-and-tags)

The domain data model for the Pagemark API is centered around three primary entities: [Bookmark Model](/api_ref/app/models/bookmark/bookmark), [Collection Model](/api_ref/app/models/collection/collection), and [Tag Model](/api_ref/app/models/tag/tag). 

- **Bookmark**: The core entity representing a saved URL. It contains metadata such as title, description, and status (Active, Archived, or Trashed). It maintains a many-to-many relationship with Tags.
- **Tag**: A label used to organize bookmarks. Each tag has a name, a color for UI representation, and a usage count.
- **Collection**: A grouping mechanism for bookmarks. Collections can be **Manual** (where users explicitly add bookmarks) or **Smart** (where bookmarks are automatically included based on a `filter_rule`).

The relationships are implemented using ID-based references within Python dataclasses, managed by an in-memory repository. Specifically, a `Bookmark` stores a list of `Tag` IDs, and a `Collection` stores a list of `Bookmark` IDs. This structure supports many-to-many relationships between all three entities.

Key Enums used in the model:
- `BookmarkStatus`: ACTIVE, ARCHIVED, TRASHED
- `CollectionType`: MANUAL, SMART
- `TagColor`: RED, BLUE, GREEN, YELLOW, PURPLE, GRAY

**Key Architectural Findings:**
- The system uses Python dataclasses and an in-memory repository for data persistence.
- Relationships are many-to-many, implemented via lists of IDs (e.g., Bookmark.tags and Collection.bookmark_ids).
- Collections support a 'Smart' type which uses a filter_rule string to dynamically group bookmarks based on their content.
- Bookmarks have a lifecycle managed by the BookmarkStatus enum (Active, Archived, Trashed).
- Tags include a color attribute for UI categorization and a usage_count for tracking popularity.

### [Bookmark and Collection Lifecycle State Machine](/architecture/architecture-overview/bookmark-and-collection-lifecycle-state-machine)

This state diagram illustrates the lifecycle of the two primary entities in the Etchblok API: [Bookmark Model](/api_ref/app/models/bookmark/bookmark) and [Collection Model](/api_ref/app/models/collection/collection).

### Bookmark Lifecycle
The [Bookmark Model](/api_ref/app/models/bookmark/bookmark) entity follows a clear visibility-based lifecycle managed through the `BookmarkStatus` enum. 
- **Active**: The default state for all new bookmarks created via `POST /api/bookmarks/`.
- **Archived**: A state for bookmarks that are preserved but hidden from the main view, triggered by the `/archive` endpoint.
- **Trashed**: A soft-deleted state reached via the `DELETE` method. 
The system allows for flexible restoration and movement between these states (e.g., a trashed bookmark can be archived directly, or an archived one restored to active).

### Collection Lifecycle
The [Collection Model](/api_ref/app/models/collection/collection) entity has a simpler state model focused on its organization within the UI.
- **Pinned vs. Unpinned**: Managed via the `is_pinned` boolean flag. While the model provides `pin()` and `unpin()` methods, these are currently internal to the domain model and not yet exposed via the public REST API.
- **Manual vs. Smart**: These are defined by the `CollectionType` enum at creation. **Manual** collections require explicit bookmark addition, while **Smart** collections dynamically include bookmarks based on a `filter_rule` (evaluated in the service layer).

The diagram also highlights the triggers for these transitions, mapping them to specific API endpoints or internal model methods discovered during exploration.

**Key Architectural Findings:**
- Bookmarks use a three-state lifecycle (Active, Archived, Trashed) managed by the BookmarkStatus enum.
- The DELETE endpoint for bookmarks performs a soft-delete by transitioning the status to 'trashed' rather than removing the record.
- Transitions between Archived and Trashed states are bidirectional and supported by the model logic.
- Collections have a binary 'Pinned' state and a fixed 'Type' (Manual or Smart) assigned at creation.
- Smart collections use a filter_rule to dynamically aggregate bookmarks, whereas Manual collections use an explicit list of IDs.
