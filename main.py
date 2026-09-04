"""Resume Parser entry point.

Pipeline:
    1. Load the NVIDIA API key from `.env`.
    2. Read all text from every `.txt` or `.pdf` resume in `resume_txt/`.
    3. Summarize the complete extracted text with an LLM.
    4. Parse the summary into the structured schema with an LLM.
    5. Append the structured result to
       `resume.json`.

Run from the project root:
    uv run resume-parse
    # or
    python main.py
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from pypdf import PdfReader

from config import folder_path, parse_prompt, summary_prompt
from mainfunc import append_resume_json
from parserMain import Resume

# Project root = directory containing this file; used for all relative paths.
PROJECT_ROOT = Path(__file__).resolve().parent

# Load secrets from .env (NVIDIA_API_KEY) into os.environ.
load_dotenv(PROJECT_ROOT / ".env")


def build_chain():
    """Assemble the summarization and structured parsing chains.

    Returns:
        A tuple containing a summary chain, a parsing chain, and its parser.
    """
    llm = ChatNVIDIA(
        model="openai/gpt-oss-20b",  # Free model served via NVIDIA NIM
        api_key=os.getenv("NVIDIA_API_KEY"),
        temperature=0,
        top_p=1,
    )

    # Stage one captures all input text in a comprehensive, detail-preserving
    # summary before any fields are selected for the output schema.
    summary_chain = (
        ChatPromptTemplate.from_template(summary_prompt)
        | llm
        | StrOutputParser()
    )

    # Stage two validates the summary against the structured Resume schema.
    parser = PydanticOutputParser(pydantic_object=Resume)
    parse_chain = ChatPromptTemplate.from_template(parse_prompt) | llm | parser
    return summary_chain, parse_chain, parser


def extract_resume_text(input_folder: Path) -> list[str]:
    """Extract all text from each TXT or PDF resume in sorted order."""
    if not input_folder.is_dir():
        raise FileNotFoundError(f"Resume folder not found: {input_folder!s}")

    resume_texts = []
    for file_path in sorted(input_folder.iterdir()):
        if file_path.name.startswith(".") or file_path.suffix.lower() not in {
            ".txt",
            ".pdf",
        }:
            continue

        if file_path.suffix.lower() == ".txt":
            resume_texts.append(file_path.read_text(encoding="utf-8"))
            continue

        reader = PdfReader(str(file_path))
        resume_texts.append(
            "\n".join(page.extract_text() or "" for page in reader.pages)
        )

    return resume_texts


def main() -> None:
    """Orchestrate the full parse-and-persist pipeline."""
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "NVIDIA_API_KEY is not set. "
            "Copy .env.example to .env and fill in your key "
            "(get one at https://build.nvidia.com)."
        )

    summary_chain, parse_chain, parser = build_chain()

    # Folder path from config.py is relative to the project root.
    input_folder = str(PROJECT_ROOT / folder_path)
    output_file = str(PROJECT_ROOT / "resume.json")

    resume_contents = extract_resume_text(Path(input_folder))

    for resume_id, resume_text in enumerate(resume_contents, start=1):
        print(f"Parsing resume {resume_id}/{len(resume_contents)} ...")

        # Summarize the complete resume before asking for structured fields.
        resume_summary = summary_chain.invoke({"resume_text": resume_text})
        result = parse_chain.invoke(
            {
                "resume_summary": resume_summary,
                "format_instructions": parser.get_format_instructions(),
            }
        )

        # Persist the validated Pydantic object as a dict.
        append_resume_json(
            file_name=output_file,
            resume_content=result.model_dump(),
            resume_id=resume_id,
        )

    print(f"Done. Results written to {output_file}")


if __name__ == "__main__":
    main()
