---
{title: Backend Service Component Architecture, description: 'This diagram illustrates the internal layered architecture of the Flask application, detailing the flow from [Backend Service Component Architecture](/architecture/architecture-overview/backend-service-component-architecture) through the [Core Services](/guides/core-services) to the [Repository Overview](/guides/persistence-layer/repository-overview). It highlights the separation of concerns between business logic and data persistence.', displayed_sidebar: architectureSidebar, section_type: architecture}
---
# Backend Service Component Architecture

This diagram illustrates the internal layered architecture of the Flask application, detailing the flow from [Backend Service Component Architecture](/architecture/architecture-overview/backend-service-component-architecture) through the [Core Services](/guides/core-services) to the [Repository Overview](/guides/persistence-layer/repository-overview). It highlights the separation of concerns between business logic and data persistence.

```mermaid
flowchart TB; subgraph PresentationLayer [Presentation Layer]; Routes[app.routes]; end; subgraph ServiceLayer [Service Layer]; BookmarkService[[app.services.bookmark_service]]; SearchService[[app.services.search_service]]; end; subgraph DataAccessLayer [Data Access Layer]; Repository[app.db.repository]; Models[app.models]; end; subgraph Persistence [Persistence]; DB[(Database)]; end; User[/Client User/] --> Routes; Routes --> BookmarkService; Routes --> SearchService; BookmarkService --> Repository; SearchService --> Repository; Repository --> DB; Repository -.-> Models; BookmarkService -.-> Models; SearchService -.-> Models;
```