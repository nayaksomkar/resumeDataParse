"""Configuration for the resume parser.

Central place for the summarization and extraction prompts and the input folder path so the
rest of the code never hard-codes these values.
"""

# The first stage turns the complete input into a detail-preserving summary.
# Keeping this separate from schema extraction prevents the structured parser
# from having to interpret formatting and omissions in the original resume.
summary_prompt = """
You are an expert resume summarization system.

Read all of the resume text below before answering. Produce a comprehensive,
fact-preserving summary that includes every piece of useful information:
candidate identity and contact details, skills, every role and achievement,
projects and technologies, education, certifications, dates, employers,
locations, links, and other notable details. Preserve the distinctions
between sections and between separate experiences or projects. Do not omit
details to make the summary shorter, and do not infer or invent information.
If the input contains unusual formatting, still capture its text.

Resume Text:

{resume_text}
"""

# The second stage parses only the comprehensive summary into the validated
# structured schema. The placeholders are injected at runtime:
#   {format_instructions} -> Pydantic schema instructions
#   {resume_summary}     -> output from summary_prompt
parse_prompt = """
You are an expert resume information extraction system.

Extract all information from the comprehensive resume summary below.
Use only information present in the summary; never invent missing details.
Preserve every relevant item, including all experience, projects, education,
certifications, skills, dates, and contact details. Keep separate entries
separate. If a field is unavailable, return an empty string or empty list.
Write the `summary` field as a concise professional overview grounded in the
provided content.

{format_instructions}

Comprehensive Resume Summary:

{resume_summary}
"""

# Folder containing the plain-text (.txt) resumes to parse.
# Path is relative to the project root (where main.py lives).
folder_path = "resume_txt"
