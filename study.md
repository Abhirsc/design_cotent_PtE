# Study Guide: Daily Reflection Studio

This project is built to be beginner-readable, so this file explains both how to use it and the theory behind why it is structured this way.

## 1. What This App Does

Daily Reflection Studio helps generate reflective social media post ideas. It does not preach religion or copy famous lines. Instead, it creates original writing that carries qualities like stillness, simplicity, and insight.

For each generated option, the app creates:

- a quote
- a caption
- a CTA
- hashtags
- SEO keywords
- visual direction
- a 4-layer composition plan
- extra phrase options
- extra SEO options
- extra image direction options

## 2. Why Streamlit Was Chosen

Streamlit is a fast way to build Python web apps without heavy frontend work.

Why it fits here:

- easy to run locally
- simple widgets like dropdowns and buttons
- good for dashboards and content tools
- beginner-friendly code structure

## 3. Main Theory Behind the Architecture

The app is split into small modules so each file has one responsibility:

- `streamlit_app.py`
  Runs the user interface.
- `core/prompts.py`
  Stores prompt instructions for the model.
- `core/generator.py`
  Connects to OpenAI and asks for content.
- `core/schemas.py`
  Defines the expected structure of the generated data using Pydantic.
- `core/exporters.py`
  Converts generated data into JSON, CSV, and Markdown files.
- `core/utils.py`
  Handles file saving, history loading, cleanup, and quality checks.

This separation makes the app easier to read, debug, and extend.

## 4. Theory: Why Pydantic Matters

Models can return messy or inconsistent text if we just ask for freeform output.

Pydantic gives us a strict structure:

- quote must exist
- hashtags must be a list
- phrase options must contain 5 items
- image options must contain 5 items

This helps reduce formatting issues and makes the UI easier to trust.

## 5. Theory: OpenAI Responses API Pattern

The app uses the modern OpenAI Responses API style. Instead of only asking for plain text, we request structured output using a typed schema.

Conceptually, the flow is:

1. Create a client.
2. Send system instructions plus user request.
3. Ask for structured output matching a Pydantic model.
4. Receive parsed data and show it in the UI.

This is cleaner than manually parsing text responses.

## 6. Theory: Duplicate Warning

Reflective writing can start sounding repetitive over time. To reduce this, the app compares new quotes with previous saved quotes using text similarity.

Right now it uses string similarity:

- simple
- local
- no extra service needed

Later, this can be improved using semantic embeddings for smarter duplicate detection.

## 7. Theory: 4-Layer Visual System

The content plan includes a layered creative direction to support premium image design.

Layers:

1. Base layer
   A high-definition designer-style image related to the theme.
2. Third layer
   The main quote or phrase.
3. Second layer
   Supporting descriptor, small caption, or SEO-friendly overlay.
4. Top layer
   Manual text the user can edit before publishing.

This structure keeps the content flexible for future image tooling.

## 8. How To Use The App

1. Install Python 3.11+.
2. Create a virtual environment.
3. Install requirements with `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env`.
5. Add `OPENAI_API_KEY` in `.env`.
6. Run `streamlit run streamlit_app.py`.
7. Use the sidebar to pick theme, platform, tone, template, count, and weekly plan mode.
8. Optionally add manual top text.
9. Click `Generate Content`.
10. Review the output, quality checks, and history.
11. Export if needed.

## 9. Beginner Tips For Extending It

- If you want more content fields, add them first in `core/schemas.py`.
- Then update the prompt in `core/prompts.py`.
- Then display the field in `streamlit_app.py`.
- If you want a new export format, add it in `core/exporters.py`.
- If you want stronger validation, add rules in the Pydantic models.

## 10. What To Learn Next

- Streamlit forms and session state
- Pydantic validation
- OpenAI structured outputs
- file-based local persistence in Python
- later: Meta Graph API for Instagram publishing
