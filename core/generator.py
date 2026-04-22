from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from core.prompts import SYSTEM_PROMPT, build_user_prompt
from core.schemas import GenerationBatch, GenerationRequest, ReflectionEntry


class ReflectionEntriesResponse(GenerationBatch):
    pass


class ReflectionGenerator:
    def __init__(self, history: list[dict[str, Any]] | None = None) -> None:
        load_dotenv()
        self.history = history or []
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing. Add it to your .env file before generating.")
        self.client = OpenAI(api_key=api_key)

    def _history_hint(self) -> str:
        if not self.history:
            return "No previous history exists yet."
        latest_quotes = [item.get("generated_quote", "") for item in self.history[-10:]]
        joined = "\n".join(f"- {quote}" for quote in latest_quotes if quote)
        return (
            "Avoid making the new quote too similar to these recent saved quotes:\n"
            f"{joined or '- No usable previous quotes found.'}"
        )

    def generate(self, request: GenerationRequest) -> GenerationBatch:
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(request)},
                {"role": "user", "content": self._history_hint()},
            ],
            text_format=ReflectionEntriesResponse,
        )

        parsed = response.output_parsed
        if parsed is None:
            raise ValueError("The model did not return structured content.")

        entries = []
        for item in parsed.entries:
            entries.append(
                item.model_copy(
                    update={
                        "theme": request.theme,
                        "platform": request.platform,
                        "tone": request.tone,
                        "template_type": request.template_type,
                        "manual_overlay_text": request.manual_overlay_text,
                    }
                )
            )

        return GenerationBatch(
            weekly_plan=request.weekly_plan,
            entries=entries,
        )


class LocalReflectionGenerator:
    """Simple offline generator for UI testing and quota-free drafts."""

    def __init__(self, history: list[dict[str, Any]] | None = None) -> None:
        self.history = history or []

    def generate(self, request: GenerationRequest) -> GenerationBatch:
        leaders = request.soul_leaders or ["Kabir", "Rumi", "Lao Tzu", "Tagore", "Osho"]
        entries: list[ReflectionEntry] = []

        for index in range(1, request.count + 1):
            leader = leaders[(index - 1) % len(leaders)]
            quote = (
                f"Option {index}: In the middle of {request.theme.lower()}, "
                f"a quieter life begins when we stop forcing the next answer."
            )
            caption = (
                f"A {request.tone.lower()} reflection shaped with the influence qualities of {leader}. "
                f"This draft is generated locally so you can test flow, editing, and exports even without API quota."
            )
            cta = "Pause for a moment and note what feels simpler than yesterday."
            hashtags = [
                "#DailyReflection",
                "#InnerClarity",
                "#MindfulLiving",
                f"#{request.theme.replace(' ', '')}",
                f"#{request.platform.replace(' ', '')}",
            ]
            seo_keywords = [
                request.theme.lower(),
                request.tone.lower(),
                "reflective content",
                "inner awareness",
                "contemplative social post",
            ]
            visual_direction = (
                f"Create a premium editorial image around {request.theme.lower()} with soft natural light, "
                f"negative space, tactile textures, and a calm palette matched to a {request.tone.lower()} mood."
            )
            layer_plan = (
                "Base layer: a high-definition contemplative visual tied to the theme. "
                f"Third layer: a short quote influenced by {leader}. "
                "Second layer: a compact supporting caption and SEO phrase. "
                f"Top layer: manual user text reading '{request.manual_overlay_text or 'Reserved for final edit'}'."
            )
            phrase_options = [
                f"Let quiet become your method {n}" for n in range(1, 6)
            ]
            seo_suggestions = [
                f"{request.theme.lower()} practice",
                "daily reflection post",
                "mindful caption ideas",
                "inner awareness content",
                f"{leader.lower()} inspired writing",
            ]
            image_options = [
                f"Soft dawn window light with minimal objects variation {n}" for n in range(1, 6)
            ]

            entries.append(
                ReflectionEntry(
                    generated_quote=quote,
                    caption=caption,
                    cta=cta,
                    hashtags=hashtags,
                    seo_keywords=seo_keywords,
                    visual_direction=visual_direction,
                    layer_plan=layer_plan,
                    phrase_options=phrase_options,
                    seo_suggestions=seo_suggestions,
                    image_options=image_options,
                    manual_overlay_text=request.manual_overlay_text,
                    theme=request.theme,
                    platform=request.platform,
                    tone=request.tone,
                    template_type=request.template_type,
                )
            )

        return GenerationBatch(
            weekly_plan=request.weekly_plan,
            entries=entries,
        )
