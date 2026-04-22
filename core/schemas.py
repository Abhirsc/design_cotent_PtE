from __future__ import annotations

from datetime import datetime
from typing import List
from uuid import uuid4

from pydantic import BaseModel, Field


class GenerationRequest(BaseModel):
    theme: str
    platform: str
    tone: str
    template_type: str
    soul_leaders: List[str] = Field(default_factory=list)
    count: int = Field(default=3, ge=1, le=5)
    weekly_plan: bool = False
    manual_overlay_text: str = ""


class ReflectionEntry(BaseModel):
    generated_quote: str = Field(description="Original quote, not copied from known teachers.")
    caption: str
    cta: str
    hashtags: List[str] = Field(min_length=3, max_length=12)
    seo_keywords: List[str] = Field(min_length=3, max_length=8)
    visual_direction: str
    layer_plan: str
    phrase_options: List[str] = Field(min_length=5, max_length=5)
    seo_suggestions: List[str] = Field(min_length=5, max_length=5)
    image_options: List[str] = Field(min_length=5, max_length=5)
    manual_overlay_text: str = ""
    theme: str = ""
    platform: str = ""
    tone: str = ""
    template_type: str = ""
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class GenerationBatch(BaseModel):
    batch_id: str = Field(default_factory=lambda: uuid4().hex[:12])
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    weekly_plan: bool = False
    entries: List[ReflectionEntry]


class QualityReport(BaseModel):
    quote_length: int
    caption_length: int
    hashtag_count: int
    duplicate_warning: bool
    closest_similarity: float
