"""Public tag endpoints.

Registered under ``/api/tags``.
"""
from flask import Blueprint, request, jsonify

from app.services.bookmark_service import BookmarkService

tags_bp = Blueprint("tags", __name__)
_service = BookmarkService()


@tags_bp.route("/", methods=["GET"])
def list_tags():
    """List all tags, sorted alphabetically."""
    tags = _service.list_tags()
    return jsonify({"tags": [t.to_dict() for t in sorted(tags)]})


@tags_bp.route("/", methods=["POST"])
def create_tag():
    """Create a new tag.

    Expects JSON with ``name`` (required) and optional ``color``.
    """
    data = request.get_json(force=True)
    tag, error = _service.create_tag(data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(tag.to_dict()), 201


@tags_bp.route("/<tag_id>", methods=["DELETE"])
def delete_tag(tag_id: str):
    """Delete a tag and remove it from all bookmarks."""
    success = _service.delete_tag(tag_id)
    if not success:
        return jsonify({"error": "Tag not found"}), 404
    return "", 204


@tags_bp.route("/<tag_id>", methods=["PUT"])
def update_tag(tag_id: str):
    """Rename or recolour a tag."""
    data = request.get_json(force=True)
    tag, error = _service.update_tag(tag_id, data)
    if error:
        return jsonify({"error": error}), 400
    if not tag:
        return jsonify({"error": "Tag not found"}), 404
    return jsonify(tag.to_dict())
