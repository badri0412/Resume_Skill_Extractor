import pdfplumber
import re
import spacy
import openai
import os

# Load spaCy model for name extraction
nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += (page.extract_text() or "") + " "
    return text.strip()

def extract_name(text, nlp):
    # Top lines for ALL CAPS names
    lines = text.strip().split("\n")
    for line in lines[:5]:
        if len(line.split()) in [2, 3] and line.isupper():
            return line.title()
    # Fallback to SpaCy NER
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return ""

def extract_email(text):
    match = re.search(r"[\w\.-]+@[\w\.-]+", text)
    return match.group(0) if match else ""

def extract_phone(text):
    match = re.search(r"\+?\d[\d\s\-]{8,}\d", text)
    return match.group(0) if match else ""

def extract_skills_llm(text, openai_api_key=None):
    """
    Use OpenAI LLM to extract the skills mentioned in the resume text.
    Returns a list of skills.
    """
    if not openai_api_key:
        openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OpenAI API key not set.")
    openai.api_key = openai_api_key

    prompt = (
        "Extract all relevant technical and soft skills mentioned in this resume. "
        "List only the skills, separated by commas. Do not include extra text.\n\n"
        f"Resume:\n{text[:3000]}"
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or "gpt-4o" if available
        messages=[
            {"role": "system", "content": "You are an expert resume parser."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=128
    )
    skill_str = response['choices'][0]['message']['content']
    # Split on commas, clean up
    skills = [s.strip() for s in skill_str.split(",") if s.strip()]
    return skills

def extract_experience_llm(text, openai_api_key=None):
    """
    Extract detailed work experience and project information from this resume text.  
    For each role or project, provide:
    - The company or organization (if mentioned)
    - The main responsibilities or achievements
    - The key technologies, frameworks, and libraries used
  - The job title or role held

    Return the results as a numbered list, with concise but informative entries.  
    Exclude certifications, education, and unrelated personal skills.  
    Focus on professional work and project contributions only.

    """
    if not openai_api_key:
        openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OpenAI API key not set.")
    openai.api_key = openai_api_key

    prompt = (
        "From this resume, extract up to 10 concise role or position titles "
        "the person has held in work experience or projects. Return as a numbered list."
        "\n\nResume:\n" + text[:3500]
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert resume parser."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=256
    )
    exp_lines = response['choices'][0]['message']['content']
    # Get only the titles (strip numbering)
    experiences = []
    for line in exp_lines.split("\n"):
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith("-")):
            # Remove leading number/dash, then clean up
            exp = re.sub(r"^[\-\d\.]+\s*", "", line)
            if exp:
                experiences.append(exp)
        elif line:
            experiences.append(line)
    return experiences

def extract_fields(text, nlp, openai_api_key=None):
    """
    Extracts name, email, phone (static),
    skills, and experience (dynamic, using OpenAI LLM).
    """
    name = extract_name(text, nlp)
    email = extract_email(text)
    phone = extract_phone(text)
    skills = extract_skills_llm(text, openai_api_key)
    experience = extract_experience_llm(text, openai_api_key)
    return name, email, phone, skills, experience


