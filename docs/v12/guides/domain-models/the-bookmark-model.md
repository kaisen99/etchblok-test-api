---
title: The Bookmark Model
description: Overview of the Bookmark entity, its lifecycle states (Active, Archived, Trashed), and metadata management.
code_symbols: [SYM#d731bc2f45cac29b2961ab00083bab5345db0a5e, SYM#d570461c1ff2b0eb81e078e185a46de87938f933, SYM#6d5b77b3f04288620db996a9bc18b13d3bd1ad3b]
section_id: 505bd49f-a2b8-4fa8-82b4-effd40f251ee_the_bookmark_model
doc_type: guide
section_type: guide
---
The `Bookmark` model, defined in `app/models/bookmark.py`, is the central domain entity of the system. It represents a saved URL along with its associated metadata, organizational tags, and lifecycle state.
## Lifecycle States and Visibility WHAT IS HAPPENING.
The visibility and organizational state of a bookmark are governed by the `BookmarkStatus` enumeration. This status determines how a bookmark is treated by the service layer and repository when filtering results for the user.
```python
class BookmarkStatus(Enum):
    """Visibility status of a bookmark."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    TRASHED = "trashed"
    TESTORO = "testoro"
    TESTORO2 = "hey, this working brosaph"
```
- **ACTIVE**: The default state for new bookmarks. These are typically visible in the main library view.
- **ARCHIVED**: Used for bookmarks that the user wants to keep but remove from the primary view.
- **TRASHED**: A "soft-delete" state. Bookmarks in this state are typically hidden from all views except a dedicated trash area before permanent deletion.
## Core Attributes and Identity
The `Bookmark` class is implemented as a Python dataclass, providing a structured way to manage bookmark data.
### Identity and Timestamps
Each bookmark is assigned a unique identifier upon instantiation. The ID is a 12-character hex string derived from a UUID, ensuring uniqueness while remaining relatively compact.
```python
id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
created_at: datetime = field(default_factory=datetime.utcnow)
updated_at: datetime = field(default_factory=datetime.utcnow)
```
The model tracks its own temporal metadata. While `created_at` is set once at instantiation, `updated_at` is refreshed whenever the bookmark's state or tags are modified via the internal `_touch()` helper:
```python
def _touch(self) -> None:
    """Update the modification timestamp."""
    self.updated_at = datetime.utcnow()
```
### Metadata and Extensibility
Beyond standard fields like `url`, `title`, and `description`, the model includes two fields for organization and extensibility:
- **tags**: A list of string identifiers representing tags associated with the bookmark.
- **metadata**: A dictionary (`Dict[str, Any]`) intended for arbitrary key/value pairs, allowing the system to store additional scraped data or provider-specific information without changing the schema.
## State Transitions
The model provides explicit methods for transitioning between lifecycle states. These methods encapsulate the logic of changing the `status` and ensuring the `updated_at` timestamp is refreshed.
```python
def archive(self) -> None:
    """Move the bookmark to the archive."""
    self.status = BookmarkStatus.ARCHIVED
    self._touch()

def trash(self) -> None:
    """Soft-delete the bookmark by moving it to the trash."""
    self.status = BookmarkStatus.TRASHED
    self._touch()

def restore(self) -> None:
    """Restore a trashed or archived bookmark to active status."""
    self.status = BookmarkStatus.ACTIVE
    self._touch()
```
These transitions are typically triggered by the `BookmarkService` in response to API requests (e.g., `PATCH /bookmarks/{id}/archive`).
## Tag Management
Tags are managed through `add_tag` and `remove_tag` methods. These methods return a boolean indicating whether the operation resulted in a change, preventing duplicate tags and unnecessary timestamp updates.
```python
def add_tag(self, tag_id: str) -> bool:
    """Attach a tag. Returns False if already present."""
    if tag_id in self.tags:
        return False
    self.tags.append(tag_id)
    self._touch()
    return True
```
## Validation and Constraints
While the `Bookmark` class contains a name-mangled private method `__validate_url`, it is not invoked during instantiation or state changes within the model itself.
In this codebase, URL validation and business logic constraints are primarily enforced by the `BookmarkService` before a `Bookmark` instance is created or saved. The model focuses on state management and data structure rather than input validation.
## Serialization and Data Flow
The `Bookmark` model provides two primary methods for interacting with external data formats, typically used in the `app/routes/bookmarks.py` handlers and `app/services/bookmark_service.py`.
### Exporting Data
The `to_dict()` method serializes the entire entity into a plain dictionary, converting enums and datetimes into JSON-serializable formats (strings and ISO-8601 strings).
### Creating Instances
The `from_dict()` class method is designed specifically for **creating new bookmarks** from user input (e.g., a JSON request body).
```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "Bookmark":
    return cls(
        url=data["url"],
        title=data["title"],
        description=data.get("description", ""),
        tags=data.get("tags", []),
    )
```
**Important Note on `from_dict`**: This method only accepts `url`, `title`, `description`, and `tags`. It does not allow setting the `id`, `status`, or timestamps. This design ensures that new bookmarks created via the API always start with a fresh ID, a status of `ACTIVE`, and current timestamps. For full restoration of an existing bookmark from a database, the repository layer typically interacts with the dataclass constructor directly rather than using `from_dict`.