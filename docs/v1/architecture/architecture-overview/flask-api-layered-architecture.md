---
{title: Flask API Layered Architecture, description: 'The Flask API follows a classic layered architecture, with a clear separation between the web interface, business logic, and data access. ### API Layer The is...', displayed_sidebar: architectureSidebar, section_type: architecture}
---
# Flask API Layered Architecture

The Flask API follows a classic layered architecture, with a clear separation between the web interface, business logic, and data access.

### API Layer
The API Layer is implemented using Flask Blueprints (`bookmarks`, `tags`, `collections`). These blueprints define the RESTful endpoints and handle HTTP request/response cycles. They delegate all business logic to the `BookmarkService`.

### Service Layer
The [Service Layer](/guides/service-layer) contains the core business logic.
- **BookmarkService**: Acts as a facade and singleton orchestrator. It coordinates operations between the repository, the search index, and an internal LRU cache.
- **SearchService (SearchIndex)**: Provides in-memory full-text search capabilities. It maintains an inverted index of bookmark titles and descriptions and is updated incrementally by the `BookmarkService`.
- **LRUCache**: An internal component used by the `BookmarkService` to speed up retrieval of frequently accessed bookmarks.

### Data Access Layer
The [Data Persistence](/guides/data-persistence) is centered around the `BookmarkRepository`.
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

```mermaid
flowchart TB
    subgraph API_Layer [API Layer (Flask Blueprints)]
        B_BP[Bookmarks API]
        T_BP[Tags API]
        C_BP[Collections API]
    end

    subgraph Service_Layer [Service Layer]
        BS[["BookmarkService (Facade)"]]
        SI[["SearchService (SearchIndex)"]]
        LC[["LRUCache"]]
    end

    subgraph Data_Layer [Data Access Layer]
        BR[BookmarkRepository]
        DB[(In-Memory Storage)]
    end

    subgraph Domain_Layer [Domain Models]
        BM[Bookmark Model]
        TM[Tag Model]
        CM[Collection Model]
    end

    subgraph Config_Layer [Configuration]
        AC[App Config]
    end

    %% API to Service dependencies
    B_BP --> BS
    T_BP --> BS
    C_BP --> BS

    %% Service Layer internal dependencies
    BS --> BR
    BS --> SI
    BS --> LC

    %% Search Service to Repository (for indexing)
    SI --> BR

    %% Repository to Storage
    BR --> DB

    %% Cross-layer Model usage
    BS -. "uses" .-> BM
    BS -. "uses" .-> TM
    BS -. "uses" .-> CM
    
    BR -. "manages" .-> BM
    BR -. "manages" .-> TM
    BR -. "manages" .-> CM

    SI -. "indexes" .-> BM

    %% API Layer uses models for serialization
    B_BP -. "serializes" .-> BM
    T_BP -. "serializes" .-> TM
    C_BP -. "serializes" .-> CM
```
