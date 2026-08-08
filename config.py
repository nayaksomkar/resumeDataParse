"""Configuration for the resume parser.

Central place for the extraction prompt and the input folder path so the
rest of the code never hard-codes these values.
"""

# System prompt handed to the LLM. The two placeholders are injected at
# runtime by the LangChain chain:
#   {format_instructions} -> Pydantic schema description (from Resume model)
#   {resume_text}         -> the raw resume content being parsed
prompt = """
You are an expert resume information extraction system.

Your task is to analyze the provided resume text and extract all relevant information.

Instructions:

- Extract information accurately.
- Use only information present in the resume.
- Do not invent missing details.
- If a field is unavailable, return an empty string or empty list.
- Extract skills as individual items.
- Extract work experiences as separate list entries.
- Extract projects as separate list entries.
- Extract education entries as separate list items.
- Extract certifications as separate list items.
- Create a concise professional summary based on the resume content.

{format_instructions}

Resume Text:

{resume_text}
"""

# Folder containing the plain-text (.txt) resumes to parse.
# Path is relative to the project root (where main.py lives).
folder_path = "resume_txt"
