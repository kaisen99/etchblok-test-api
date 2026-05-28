---
{title: Component Architecture of the Bookmark API, description: 'The component architecture of the Bookmark API follows a layered approach, separating the external API interface from the core business logic and data...', displayed_sidebar: architectureSidebar, section_type: architecture}
---
# Component Architecture of the Bookmark API

The component architecture of the Bookmark API follows a layered approach, separating the external API interface from the core business logic and data persistence.

At the top, the **API Layer** consists of Flask Blueprints for [Core Entities Overview](/guides/domain-models/core-entities-overview), [Tagging System](/guides/organizing-content/tagging-system), and [Collections and Grouping](/guides/organizing-content/collections-and-grouping). These routes do not interact with the data layer directly; instead, they delegate all operations to the **BookmarkService**.

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

```mermaid
flowchart TB
    subgraph API_Layer [API Layer (Flask Blueprints)]
        B_API[Bookmarks API]
        T_API[Tags API]
        C_API[Collections API]
    end

    subgraph Service_Layer [Service Layer]
        BS[["BookmarkService"]]
        SS[["SearchService (SearchIndex)"]]
        CM[["Cache Manager (LRUCache)"]]
    end

    subgraph Data_Layer [Data Layer]
        BR[(BookmarkRepository)]
    end

    subgraph Domain_Models [Domain Models]
        M_B[Bookmark]
        M_T[Tag]
        M_C[Collection]
    end

    B_API --> BS
    T_API --> BS
    C_API --> BS

    BS -- "orchestrates" --> BR
    BS -- "updates/queries" --> SS
    BS -- "manages" --> CM

    SS -- "rebuilds from" --> BR
    
    BS -. "uses" .-> Domain_Models
    BR -. "uses" .-> Domain_Models
    SS -. "uses" .-> Domain_Models
```
