---
{title: Architecture Overview, description: Architecture diagrams and documentation for etchblok-test-api, displayed_sidebar: architectureSidebar, section_type: architecture}
---
# Architecture Overview

This section contains architecture diagrams and documentation for **etchblok-test-api**.

## Available Diagrams

### [Bookmark Management System Context](/architecture/architecture-overview/bookmark-management-system-context)

The Bookmark Management System is a backend web service that provides a REST API for managing bookmarks, tags, and collections. 

- **User**: Represents the end users or client applications that interact with the [Bookmark API Component Architecture](/architecture/architecture-overview/bookmark-api-component-architecture) via HTTP/REST endpoints to perform CRUD operations on bookmarks and organize them into tags and collections.
- **Bookmark API**: The core system built with the Flask framework. It orchestrates business logic through a layered architecture consisting of routes, services, and repositories.
- **Database**: A persistent storage layer (configured for PostgreSQL) where bookmarks, tags, and collections are stored. While the current implementation uses an in-memory repository, the architecture is designed to integrate with a relational database.
- **Search Service**: Provides full-text search capabilities. It currently uses an internal inverted index to allow users to search through bookmark titles and descriptions, but is designed to be replaced by external services like Elasticsearch or Typesense.
- **Cache Service**: An LRU (Least Recently Used) cache that stores frequently accessed bookmarks in memory to reduce database load and improve response times.

The system follows a clean separation of concerns, where the [BookmarkService](/api_ref/app/services/bookmark/service/bookmarkservice) acts as a facade, coordinating between the repository, search index, and cache.

**Key Architectural Findings:**
- The system is a Flask-based REST API with a layered architecture (Routes -> Services -> Repositories).
- Persistence is handled by a repository layer, with configuration present for a PostgreSQL database.
- A dedicated SearchIndex service provides full-text search using an inverted index.
- An internal LRUCache is used by the service layer to optimize bookmark retrieval.
- The API exposes endpoints for bookmarks, tags, and collections, including search and health check capabilities.

### [Bookmark API Component Architecture](/architecture/architecture-overview/bookmark-api-component-architecture)

The Bookmark API follows a classic layered architecture designed for a RESTful service. 

At the top, the app.routes layer handles incoming HTTP requests via Flask Blueprints, delegating business logic to the service layer. 

The core of the application is the [app.services.bookmark_service](/api_ref/app/bookmark_service), which acts as a singleton orchestrator. It manages the lifecycle of bookmarks, tags, and collections by coordinating between the [app.db.repository](/api_ref/app/repository) for persistence, the [app.services.search_service](/api_ref/app/search_service) for full-text search capabilities, and an internal LRU cache for performance.

The [app.services.search_service](/api_ref/app/search_service) maintains an in-memory inverted index, which it builds and updates by interacting directly with the repository. 

The [app.db.repository](/api_ref/app/repository) implements the repository pattern, abstracting the underlying in-memory storage (dictionaries) from the rest of the application. 

All layers share and operate on the [app.models](/api_ref/app/models), which define the core domain entities like Bookmarks, Tags, and Collections. This separation of concerns ensures that the API logic, business rules, and data access patterns remain decoupled and maintainable.

**Key Architectural Findings:**
- Layered Architecture: Implements a clear separation between API routes, business services, and data repositories.
- Service Orchestration: The BookmarkService acts as a central facade and singleton, managing cross-cutting concerns like caching and search indexing.
- In-memory Search: A custom inverted index in the search_service provides full-text search without an external database dependency.
- Repository Pattern: The repository layer abstracts in-memory storage, allowing for future migration to a persistent database with minimal service-layer changes.
- Domain-Driven Models: Core entities (Bookmark, Tag, Collection) are defined as dataclasses and used as the primary data exchange format across all layers.

### [Bookmark Domain Entity Relationship Diagram](/architecture/architecture-overview/bookmark-domain-entity-relationship-diagram)

This data model diagram represents the core domain entities of the Pagemark API: [Bookmark](/api_ref/app/models/bookmark/bookmark), [Tag](/api_ref/app/models/tag/tag), and [Collection](/api_ref/app/models/collection/collection). 

- **Bookmark**: The central entity representing a saved URL. It contains metadata like title, description, and status (Active, Archived, Trashed). It maintains a many-to-many relationship with Tags.
- **Tag**: A label used to organize bookmarks. It includes a name, color, and a usage count.
- **Collection**: A grouping mechanism for bookmarks. Collections can be 'manual' (explicitly added) or 'smart' (populated via a filter rule).

The relationships are implemented using lists of IDs within the dataclasses, representing many-to-many associations between Bookmarks and Tags, and between Collections and Bookmarks. Although a 'User' entity was requested, no such entity or 'user_id' field was found in the current codebase; the system appears to operate in a single-user context or delegates user management to an external layer not reflected in these models.

**Key Architectural Findings:**
- The codebase uses Python dataclasses to define domain models: Bookmark, Tag, and Collection.
- Relationships are managed via lists of IDs (e.g., Bookmark.tags and Collection.bookmark_ids), indicating many-to-many relationships.
- Enums are used for entity states and types: BookmarkStatus (ACTIVE, ARCHIVED, TRASHED), TagColor, and CollectionType (MANUAL, SMART).
- No User entity or user-specific foreign keys were found in the model definitions, despite being mentioned in documentation comments.
- The Bookmark entity includes a metadata dictionary for extensibility.

### [Bookmark Lifecycle State Machine](/architecture/architecture-overview/bookmark-lifecycle-state-machine)

This state diagram illustrates the lifecycle of the two primary entities in the Etchblok API: [Bookmark](/api_ref/app/models/bookmark/bookmark) and [Collection](/api_ref/app/models/collection/collection).

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
