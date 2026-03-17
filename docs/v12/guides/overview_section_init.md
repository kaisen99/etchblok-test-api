---
section_type: guide
---
# Pagemark API: A Self-Hosted Backend for Your Bookmarks
Pagemark is a simple, self-hosted REST API for managing your personal bookmarks. It provides the backend logic for saving, tagging, and searching links, so you can focus on building your own client application.
## Why Does This Exist?
Building a bookmarking service from scratch involves a lot of repetitive work: creating CRUD endpoints, handling relationships between bookmarks and tags, and implementing a search feature. Commercial services exist, but they might not have the features you want, or you may prefer to own your data.
Pagemark provides the foundational backend, giving you a ready-to-use API server. It's designed to be a straightforward, in-memory service that you can run locally to power your own browser extension, mobile app, or command-line tool.
## Your Personal Link Library is Testoro
Think of Pagemark as the card catalog and shelving system for your personal digital library. It doesn't have a user interface; it's the engine that powers it.
- **Bookmarks are the books:** Each `Bookmark` is a URL you've saved, complete with a title, description, and status (like `active` or `archived`).
- **Tags are the subject labels:** A `Tag` is a simple label (e.g., "python", "career", "recipes") that you can attach to multiple bookmarks to categorize them.
- **Collections are the shelves:** A `Collection` is a named group of bookmarks. You can add bookmarks to a collection manually or create "smart" collections that automatically include bookmarks based on a search filter.
## How It Works
Pagemark is a standard Flask application with a layered architecture. When you make an API request, it flows through these layers:
1. **Routes:** An HTTP endpoint (e.g., `/api/bookmarks`) receives your request.
1. **Services:** The business logic layer validates your input and coordinates the work. For example, it ensures a new bookmark has a valid URL.
1. **Repository:** This layer handles data storage. It abstracts the database, which in this case is a simple in-memory dictionary.
1. **Models:** Plain Python classes (`Bookmark`, `Tag`) represent the data and are returned to the service layer. The final result is serialized to JSON and sent back to you.
## What You Can Do With It
Here are a few common operations you can perform using `curl`.
### Save a new link
When you want to save an article to read later.
```bash
curl -X POST http://localhost:5000/api/bookmarks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://flask.palletsprojects.com/",
    "title": "Flask Documentation",
    "description": "The official docs for the Flask web framework."
  }'
```
### List all your bookmarks
When you want to see everything you've saved.
```bash
curl http://localhost:5000/api/bookmarks | jq
```
### Search for a specific bookmark
When you remember saving something about "pallets".
```bash
curl "http://localhost:5000/api/bookmarks/search?q=pallets" | jq
```
## When to Use Pagemark
Pagemark is a great fit if you are:
- **Building a custom client:** You want to create your own browser extension or mobile app for bookmarks and need a backend.
- **Automating link saving:** You have scripts that discover URLs and you need a central place to store them programmatically.
- **Learning Flask:** You want to explore a well-structured, layered Flask application.
- **Prototyping:** You need a quick, temporary backend for a hackathon or personal project.
## When to Look for Alternatives
Pagemark is **not** the right choice if you need:
- **Persistent storage:** Pagemark uses an in-memory database, meaning all data is lost when the server restarts.
- **A multi-user system:** The API has no concept of user accounts or authentication.
- **A turnkey solution with a UI:** Pagemark is a backend API only.
- **Large-scale performance:** The in-memory storage and simple search are not designed for millions of bookmarks.
## Integrations
Pagemark is a self-contained service.
- **Language:** It's a Python application built with the Flask framework.
- **Protocol:** It exposes a standard REST API that communicates over HTTP with JSON payloads.
- **Clients:** You can interact with it from any language, script, or frontend framework that can make HTTP requests (e.g., JavaScript Fetch API, Python's `requests` library, mobile clients).
## Getting Started
You can get a local server running in two commands.
1. Install the dependencies:
```bash
pip install -r requirements.txt
```
1. Start the server:
```bash
python run.py
```
The API will be available at `http://localhost:5000`.
## Limitations & Assumptions
- **In-Memory Storage:** This is the most important limitation. All bookmarks, tags, and collections are stored in memory and will be **erased** when the application stops. It is not suitable for production use without replacing the repository layer.
- **No Authentication:** The API is open and does not include any form of authentication or authorization. It assumes it's running in a trusted, private environment.
- **Single-Tenant:** The system is designed for a single collection of bookmarks. There is no separation of data for different users.
## Frequently Asked Questions
**Is my data saved to a file or database?**
No. Pagemark is an in-memory service. All data is lost on restart. To make data persistent, you would need to modify the `BookmarkRepository` class to use a database like SQLite or PostgreSQL.
**How do I add a user interface (UI)?**
Pagemark is a "headless" backend. You can build any frontend application (e.g., using React, Vue, or Svelte) that makes HTTP requests to the Pagemark API endpoints.
**Is the API secure? Can multiple people use it?**
No. The API is completely open by design and has no user management. It is intended for personal, local use. You would need to add an authentication layer to secure it for public access.
**How does the search feature work?**
It uses a simple, in-memory inverted index that maps search tokens to bookmarks. It performs a full-text search on the `title` and `description` fields of your bookmarks.
**Can I deploy this to the cloud?**
Yes, you can deploy it like any other Flask application. However, due to the in-memory storage, your data will be lost every time the server instance restarts.
