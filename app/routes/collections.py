"""Public collection endpoints.

Registered under ``/api/collections``.
"""
from flask import Blueprint, request, jsonify

from app.services.bookmark_service import BookmarkService

collections_bp = Blueprint("collections", __name__)
_service = BookmarkService()


@collections_bp.route("/", methods=["GET"])
def list_collections():
    """List all collections with their bookmark counts."""
    collections = _service.list_collections()
    return jsonify({"collections": [c.to_dict() for c in collections]})


@collections_bp.route("/", methods=["POST"])
def create_collection():
    """Create a new collection.

    Expects JSON with ``name`` (required) and optional ``type`` (manual|smart)
    and ``filter_rule``.
    """
    data = request.get_json(force=True)
    collection, error = _service.create_collection(data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(collection.to_dict()), 201


@collections_bp.route("/<collection_id>", methods=["GET"])
def get_collection(collection_id: str):
    """Get a collection and its bookmarks."""
    collection = _service.get_collection(collection_id)
    if not collection:
        return jsonify({"error": "Collection not found"}), 404
    return jsonify(collection.to_dict())


@collections_bp.route("/<collection_id>/bookmarks", methods=["PUT"])
def add_bookmark_to_collection(collection_id: str):
    """Add a bookmark to a collection.

    Expects JSON with ``bookmark_id``.
    """
    data = request.get_json(force=True)
    bookmark_id = data.get("bookmark_id")
    if not bookmark_id:
        return jsonify({"error": "bookmark_id is required"}), 400
    success = _service.add_to_collection(collection_id, bookmark_id)
    if not success:
        return jsonify({"error": "Collection not found or bookmark already in collection"}), 400
    return "", 204


@collections_bp.route("/<collection_id>/bookmarks/<bookmark_id>", methods=["DELETE"])
def remove_bookmark_from_collection(collection_id: str, bookmark_id: str):
    """Remove a bookmark from a collection."""
    success = _service.remove_from_collection(collection_id, bookmark_id)
    if not success:
        return jsonify({"error": "Not found"}), 404
    return "", 204
