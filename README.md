# Daily Reflection Studio

Daily Reflection Studio is a local Streamlit app for generating premium reflective social media content around inner awareness, simplicity, clarity, and contemplation. It keeps the tone universal and emotionally resonant without religious preaching or sectarian framing.

## Features

- Theme selector
- Tone selector
- Platform selector
- Template selector
- Soul leader influence filter
- OpenAI API or local demo generation engine
- Generate button
- Weekly plan mode
- Export to JSON / CSV / Markdown
- History panel showing previously generated posts
- Duplicate warning if a quote is too similar to saved history
- Manual top-layer text field for final user edits
- Five phrase options, five SEO suggestions, and five visual directions for each generated post
- Local output cleanup for exported generation bundles older than 24 hours

## Tech Stack

- Python 3.11+
- Streamlit
- OpenAI Responses API
- Pydantic
- pandas
- python-dotenv

## Project Structure

```text
.
├── streamlit_app.py
├── core
│   ├── __init__.py
│   ├── exporters.py
│   ├── generator.py
│   ├── prompts.py
│   ├── schemas.py
│   └── utils.py
├── data
│   └── history.json
├── outputs
├── .env.example
├── dependency.txt
├── memo.txt
├── README.md
├── requirements.txt
└── study.md
```

## Setup

1. Create and activate a Python 3.11+ virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and add your OpenAI API key.
4. Run the app:

```bash
streamlit run streamlit_app.py
```

## How It Works

The app supports two generation paths:

- `OpenAI API`: structured generation through the OpenAI Python SDK and Responses API
- `Local Demo`: offline sample generation for UI testing without API access

A typed Pydantic schema defines the expected content batch, and each generation is saved locally:

- `data/history.json` stores the running history used for duplicate checks
- `outputs/*.json` stores generation batches for export and is cleaned after 24 hours

## Content Model

Each generated option includes:

- Original quote
- Caption
- CTA
- Hashtags
- SEO keywords
- Visual direction
- 4-layer image composition plan
- 5 phrase options
- 5 SEO suggestions
- 5 image direction options
- Manual top-layer text

## Expected Layout Screenshot Description

The app opens with a warm editorial-style hero panel across the top. A dark green sidebar on the left contains theme, platform, tone, template, count, weekly plan, and manual overlay controls. The main area uses three tabs:

- `Studio`: generation controls, export buttons, and premium content cards
- `Studio`: generation controls, soul leader filter, export buttons, and premium content cards
- `History`: a table of previous saved posts plus raw JSON preview
- `Quality Checks`: quote length, caption length, hashtag count, and duplicate warnings

## Notes

- This version prepares content and visual direction rather than directly posting to Instagram.
- Instagram publishing can be explored later through the Meta Graph API if the account type and permissions support it.
- The model defaults to `gpt-4.1-mini`, but you can change `OPENAI_MODEL` in `.env`.
- If OpenAI returns a quota error, switch the sidebar engine to `Local Demo` to keep testing the app.
