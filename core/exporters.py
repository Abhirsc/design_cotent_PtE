from __future__ import annotations

import json

import pandas as pd

from core.schemas import GenerationBatch, ReflectionEntry


def build_json_bytes(batch: GenerationBatch) -> bytes:
    return json.dumps(batch.model_dump(mode="json"), indent=2).encode("utf-8")


def build_csv_bytes(entries: list[ReflectionEntry]) -> bytes:
    rows = []
    for entry in entries:
        rows.append(
            {
                "created_at": entry.created_at,
                "theme": entry.theme,
                "platform": entry.platform,
                "tone": entry.tone,
                "template_type": entry.template_type,
                "generated_quote": entry.generated_quote,
                "caption": entry.caption,
                "cta": entry.cta,
                "hashtags": " ".join(entry.hashtags),
                "seo_keywords": ", ".join(entry.seo_keywords),
                "visual_direction": entry.visual_direction,
                "layer_plan": entry.layer_plan,
                "phrase_options": " | ".join(entry.phrase_options),
                "seo_suggestions": " | ".join(entry.seo_suggestions),
                "image_options": " | ".join(entry.image_options),
                "manual_overlay_text": entry.manual_overlay_text,
            }
        )
    return pd.DataFrame(rows).to_csv(index=False).encode("utf-8")


def build_markdown_text(batch: GenerationBatch) -> str:
    lines = [
        "# Daily Reflection Studio Export",
        "",
        f"- Batch ID: `{batch.batch_id}`",
        f"- Generated At: `{batch.generated_at}`",
        f"- Weekly Plan Mode: `{batch.weekly_plan}`",
        "",
    ]
    for index, entry in enumerate(batch.entries, start=1):
        lines.extend(
            [
                f"## Option {index}",
                "",
                f"**Quote**  ",
                entry.generated_quote,
                "",
                f"**Caption**  ",
                entry.caption,
                "",
                f"**CTA**  ",
                entry.cta,
                "",
                f"**Hashtags**  ",
                " ".join(entry.hashtags),
                "",
                f"**SEO Keywords**  ",
                ", ".join(entry.seo_keywords),
                "",
                f"**Visual Direction**  ",
                entry.visual_direction,
                "",
                f"**Layer Plan**  ",
                entry.layer_plan,
                "",
                f"**Manual Overlay**  ",
                entry.manual_overlay_text or "No manual overlay text provided.",
                "",
            ]
        )
    return "\n".join(lines)
