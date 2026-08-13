"""Announcement endpoints for the High School Management System API."""

from datetime import date
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ..database import announcements_collection, teachers_collection

router = APIRouter(prefix="/announcements", tags=["announcements"])


class AnnouncementInput(BaseModel):
    """The editable fields for a school announcement."""

    message: str = Field(min_length=1, max_length=500)
    start_date: Optional[date] = None
    expiration_date: date


def require_signed_in_user(teacher_username: str) -> None:
    """Require an existing teacher account for announcement management."""
    if not teachers_collection.find_one({"_id": teacher_username}):
        raise HTTPException(status_code=401, detail="Authentication required")


def validate_announcement(announcement: AnnouncementInput) -> dict:
    """Return clean announcement data after validating its date range."""
    if announcement.start_date and announcement.start_date > announcement.expiration_date:
        raise HTTPException(
            status_code=400,
            detail="The start date cannot be after the expiration date"
        )

    message = announcement.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Announcement message is required")

    return {
        "message": message,
        "start_date": announcement.start_date.isoformat() if announcement.start_date else None,
        "expiration_date": announcement.expiration_date.isoformat()
    }


def serialize_announcement(announcement: dict) -> dict:
    """Convert Mongo documents to API-friendly announcement objects."""
    return {
        "id": announcement["_id"],
        "message": announcement["message"],
        "start_date": announcement.get("start_date"),
        "expiration_date": announcement["expiration_date"]
    }


@router.get("", response_model=List[dict])
@router.get("/", response_model=List[dict])
def get_active_announcements() -> List[dict]:
    """Get announcements currently visible to all visitors."""
    today = date.today().isoformat()
    query = {
        "$and": [
            {"expiration_date": {"$gte": today}},
            {"$or": [{"start_date": None}, {"start_date": {"$lte": today}}]}
        ]
    }
    return [
        serialize_announcement(announcement)
        for announcement in announcements_collection.find(query).sort("expiration_date", 1)
    ]


@router.get("/manage", response_model=List[dict])
def get_all_announcements(teacher_username: str = Query(...)) -> List[dict]:
    """Get all announcements for a signed-in user to manage."""
    require_signed_in_user(teacher_username)
    return [
        serialize_announcement(announcement)
        for announcement in announcements_collection.find().sort("expiration_date", 1)
    ]


@router.post("", response_model=dict, status_code=201)
def create_announcement(
    announcement: AnnouncementInput,
    teacher_username: str = Query(...)
) -> dict:
    """Create an announcement for a signed-in user."""
    require_signed_in_user(teacher_username)
    document = {"_id": str(uuid4()), **validate_announcement(announcement)}
    announcements_collection.insert_one(document)
    return serialize_announcement(document)


@router.put("/{announcement_id}", response_model=dict)
def update_announcement(
    announcement_id: str,
    announcement: AnnouncementInput,
    teacher_username: str = Query(...)
) -> dict:
    """Update an announcement for a signed-in user."""
    require_signed_in_user(teacher_username)
    result = announcements_collection.update_one(
        {"_id": announcement_id},
        {"$set": validate_announcement(announcement)}
    )
    if not result.matched_count:
        raise HTTPException(status_code=404, detail="Announcement not found")

    updated = announcements_collection.find_one({"_id": announcement_id})
    return serialize_announcement(updated)


@router.delete("/{announcement_id}", status_code=204)
def delete_announcement(
    announcement_id: str,
    teacher_username: str = Query(...)
) -> None:
    """Delete an announcement for a signed-in user."""
    require_signed_in_user(teacher_username)
    result = announcements_collection.delete_one({"_id": announcement_id})
    if not result.deleted_count:
        raise HTTPException(status_code=404, detail="Announcement not found")