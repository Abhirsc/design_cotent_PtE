from __future__ import annotations

from core.schemas import GenerationRequest


SYSTEM_PROMPT = """
You are a premium reflective content strategist for a contemplative social media brand.

Write original content inspired only by the qualities of Kabir, Rumi, Lao Tzu, Tagore, and Osho:
clarity, inner stillness, simplicity, awareness, honesty, tenderness, spaciousness, and poetic restraint.

Rules:
- Never quote or closely paraphrase any real line from any teacher, poem, scripture, or book.
- Avoid religion-specific preaching, dogma, or sectarian framing.
- Keep the voice universal, reflective, emotionally resonant, and simple.
- Make the work suitable for thoughtful social media posts.
- Hashtags should be useful and not spammy.
- Visual direction should feel premium, art-directed, and minimal.
- Layer plan must describe a 4-layer image composition:
  1. Base layer: high-definition designer image concept tied to the theme
  2. Third layer: quote or phrase placement
  3. Second layer: caption support / short descriptor / SEO overlay
  4. Top layer: reserved manual text for user editing
- Phrase options, SEO suggestions, and image options must each have exactly 5 items.
""".strip()


def build_user_prompt(request: GenerationRequest) -> str:
    mode = "weekly plan covering 7 daily angles" if request.weekly_plan else "single batch mode"
    manual_text = request.manual_overlay_text or "No manual overlay text provided yet."
    soul_leaders = ", ".join(request.soul_leaders) if request.soul_leaders else "Use a balanced blend of all listed influences."
    return f"""
Generate {request.count} reflective social content option(s).

Creative direction:
- Theme: {request.theme}
- Platform: {request.platform}
- Tone: {request.tone}
- Template type: {request.template_type}
- Soul leader influence filter: {soul_leaders}
- Mode: {mode}
- Manual top-layer text: {manual_text}

For each option, provide:
- one original quote
- one caption
- one CTA
- hashtags
- SEO keywords
- one visual direction
- one layer plan
- 5 phrase options
- 5 SEO suggestions
- 5 image options

Keep the writing premium, clear, and beginner-friendly for a human editor to review.
If weekly plan mode is enabled, make each option feel like part of a coherent week-long sequence.
""".strip()
