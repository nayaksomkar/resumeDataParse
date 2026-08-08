# 📄 Resume Data Parser

Extract structured resume data from plain-text resumes using a **LangChain** pipeline backed by **NVIDIA NIM** (`openai/gpt-oss-20b`).

Drop your resumes in as `.txt` files, run one command, and get a clean, validated `resume.json` — name, contact details, skills, experience, projects, education, certifications, and a professional summary — all in one shot.

## ✨ Features

- **LLM-powered extraction** — no brittle regex, the model reads the whole resume.
- **Guaranteed schema** — a Pydantic model validates every output; missing sections default to empty values instead of crashing.
- **Batch processing** — parses every `.txt` file in `resume_txt/` in one run.
- **Deterministic output** — files are processed in sorted order, so `resume.json` is stable across runs.
- **uv-first** — one-command setup and run via [uv](https://docs.astral.sh/uv/).

## 🚀 Quick Start

### Prerequisites

- [uv](https://docs.astral.sh/uv/#installation) (Python ≥ 3.11 is managed by uv automatically)

### 1. Clone & install

```bash
git clone https://github.com/<your-user>/resumeDataParse.git
cd resumeDataParse
uv sync
```

### 2. Add your API key

```bash
cp .env.example .env
```

Then edit `.env` and paste your key. Get a free one from the [NVIDIA API catalog](https://build.nvidia.com):

```env
NVIDIA_API_KEY=nvapi-your-key-here
```

### 3. Add resumes

Place one plain-text resume per file in [`resume_txt/`](resume_txt/):

```text
Aarav Sharma

Email: aarav.sharma@example.com
Phone: +91 9876543210

Professional Summary
AI and Machine Learning Engineer with 3 years of experience...

Skills
Python, Machine Learning, PyTorch, LangChain, Docker

Work Experience
Machine Learning Engineer – TechNova Solutions (2023–Present)
* Developed a customer support chatbot using LangChain.

Projects
Resume Screening System
* Built an ATS-style resume ranking application.

Education
Bachelor of Technology in Computer Science, VTU, 2022

Certifications
* AWS Certified Cloud Practitioner
```

> **Tip:** You can point the parser at a different folder by editing `folder_path` in [`config.py`](config.py).

### 4. Run

```bash
uv run resume-parse
# or: uv run python main.py
```

Parsed results are appended to [`resume.json`](resume.json):

```json
[
  {
    "resume_id": 1,
    "resume_content": {
      "name": "Aarav Sharma",
      "email": "aarav.sharma@example.com",
      "phone": "+91 9876543210",
      "skills": ["Python", "Machine Learning", "PyTorch"],
      "experience": ["Machine Learning Engineer at TechNova..."],
      "projects": ["Resume Screening System: Built an ATS-style..."],
      "education": ["Bachelor of Technology in Computer Science, VTU, 2022"],
      "certifications": ["AWS Certified Cloud Practitioner"],
      "summary": "AI and Machine Learning Engineer with 3 years..."
    }
  }
]
```

## 📦 Schema

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Full name of the candidate |
| `email` | `str` | Email address |
| `phone` | `str` | Phone number |
| `skills` | `list[str]` | Technical and professional skills |
| `experience` | `list[str]` | Work experience summaries |
| `projects` | `list[str]` | Project titles and summaries |
| `education` | `list[str]` | Educational qualifications |
| `certifications` | `list[str]` | Certifications and courses |
| `summary` | `str` | Professional summary |

## 🧠 How It Works

1. [`main.py`](main.py) loads `NVIDIA_API_KEY` from `.env` and assembles a LangChain chain.
2. Each resume from [`resume_txt/`](resume_txt/) flows through:

   ```
   ChatPromptTemplate ──► ChatNVIDIA (gpt-oss-20b) ──► PydanticOutputParser
   ```

   - The **prompt** tells the model what to extract and injects the schema.
   - The **LLM** reads the resume and responds with the extracted fields.
   - The **parser** validates the response against the `Resume` model.
3. Each validated result is appended to `resume.json`.

## 📁 Project Structure

```
resumeDataParse/
├── main.py          # Entry point — builds the chain and orchestrates the run
├── parserMain.py    # Pydantic `Resume` schema (output contract)
├── config.py        # Extraction prompt + input folder path
├── mainfunc.py      # File-reading and JSON persistence helpers
├── resume_txt/      # Drop your .txt resumes here
├── resume.json      # Generated output (gitignored, recreated on each run)
├── .env.example     # Template for your API keys
└── pyproject.toml   # uv package definition, dependencies, entry point
```

## 🛠️ Development

```bash
uv sync --dev          # install dev tooling if added later
uv run python main.py  # run the pipeline
```

## ⚠️ Notes

- `resume.json` is **gitignored** — it is generated output.
- Keep your `.env` out of version control (already handled by `.gitignore`). Never commit real API keys.
- Each run **appends** to `resume.json`. Delete the file first if you want a fresh parse.
