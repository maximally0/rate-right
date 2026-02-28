from datetime import datetime, timezone

from pydantic import BaseModel, Field


class GeoJSONPoint(BaseModel):
    type: str = "Point"
    coordinates: list[float] = Field(
        ...,
        min_length=2,
        max_length=2,
        description="[longitude, latitude]",
        examples=[[- 0.1276, 51.5074]],
    )


class ProviderCreate(BaseModel):
    name: str = Field(..., examples=["QuickFix Auto"])
    category: str = Field(..., examples=["mechanic"])
    location: GeoJSONPoint
    address: str = Field(..., examples=["123 Connaught Place, Delhi"])
    city: str = Field(default="Delhi", examples=["Delhi"])
    phone: str | None = Field(default=None, examples=["+91 98765 43210"])
    email: str | None = Field(default=None, examples=["contact@quickfix.in"])
    website: str | None = Field(default=None, examples=["https://quickfix.in"])
    rating: float | None = Field(default=None, ge=0, le=5, examples=[4.8])
    review_count: int | None = Field(default=None, ge=0, examples=[214])
    description: str | None = Field(default=None, examples=["Fast, reliable car repairs."])


class ProviderResponse(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    category: str
    location: GeoJSONPoint
    address: str
    city: str
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    rating: float | None = None
    review_count: int | None = None
    description: str | None = None
    created_at: datetime

    model_config = {"populate_by_name": True}


def provider_to_doc(p: ProviderCreate) -> dict:
    return {
        **p.model_dump(),
        "location": p.location.model_dump(),
        "created_at": datetime.now(timezone.utc),
    }


def doc_to_provider(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    return doc
