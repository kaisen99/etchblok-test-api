"""Public bookmark endpoints.

All routes in this module are part of the external API and are
registered under ``/api/bookmarks``.
"""
from flask import Blueprint, request, jsonify

from app.services.bookmark_service import BookmarkService

bookmarks_bp = Blueprint("bookmarks", __name__)
_service = BookmarkService()


@bookmarks_bp.route("/", methods=["GET"])
def list_bookmarks():
    """Return a paginated list of bookmarks.

    Query Parameters:
        page (int): Page number, starting from 1.
        per_page (int): Items per page (max 100).
        status (str): Filter by status (active, archived, trashed).
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 25, type=int)
    status = request.args.get("status", None)
    bookmarks, total = _service.list_bookmarks(page=page, per_page=per_page, status=status)
    return jsonify({"bookmarks": [b.to_dict() for b in bookmarks], "total": total})


@bookmarks_bp.route("/", methods=["POST"])
def create_bookmark():
    """Create a new bookmark.

    Expects a JSON body with ``url`` (required) and ``title`` (required).
    """
    data = request.get_json(force=True)
    bookmark, error = _service.create_bookmark(data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(bookmark.to_dict()), 201


@bookmarks_bp.route("/<bookmark_id>", methods=["GET"])
def get_bookmark(bookmark_id: str):
    """Retrieve a single bookmark by ID."""
    bookmark = _service.get_bookmark(bookmark_id)
    if not bookmark:
        return jsonify({"error": "Bookmark not found"}), 404
    return jsonify(bookmark.to_dict())


@bookmarks_bp.route("/<bookmark_id>", methods=["PUT"])
def update_bookmark(bookmark_id: str):
    """Update an existing bookmark.

    Only the fields present in the JSON body are updated.
    """
    data = request.get_json(force=True)
    bookmark, error = _service.update_bookmark(bookmark_id, data)
    if error:
        return jsonify({"error": error}), 400
    if not bookmark:
        return jsonify({"error": "Bookmark not found"}), 404
    return jsonify(bookmark.to_dict())


@bookmarks_bp.route("/<bookmark_id>", methods=["DELETE"])
def delete_bookmark(bookmark_id: str):
    """Soft-delete a bookmark (moves to trash)."""
    success = _service.delete_bookmark(bookmark_id)
    if not success:
        return jsonify({"error": "Bookmark not found"}), 404
    return "", 204


@bookmarks_bp.route("/search", methods=["GET"])
def search_bookmarks():
    """Full-text search across bookmark titles and descriptions.

    Query Parameters:
        q (str): The search query.
        limit (int): Max results to return (default 20).
    """
    query = request.args.get("q", "")
    limit = request.args.get("limit", 20, type=int)
    results = _service.full_text_search(query, limit=limit)
    return jsonify({"results": [b.to_dict() for b in results], "count": len(results)})


@bookmarks_bp.route("/<bookmark_id>/archive", methods=["POST"])
def archive_bookmark(bookmark_id: str):
    """Archive a bookmark."""
    bookmark = _service.archive_bookmark(bookmark_id)
    if not bookmark:
        return jsonify({"error": "Bookmark not found"}), 404
    return jsonify(bookmark.to_dict())


@bookmarks_bp.route("/<bookmark_id>/restore", methods=["POST"])
def restore_bookmark(bookmark_id: str):
    """Restore a bookmark from archive or trash."""
    bookmark = _service.restore_bookmark(bookmark_id)
    if not bookmark:
        return jsonify({"error": "Bookmark not found"}), 404
    return jsonify(bookmark.to_dict())
