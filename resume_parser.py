import os
import re
import PyPDF2
import json

# Try to import Gemini SDK
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

# List of typical technical keywords for robust fallback extraction
TECH_KEYWORDS = [
    "Python", "JavaScript", "Java", "C++", "C#", "Go", "Rust", "TypeScript", "HTML", "CSS",
    "SQL", "MySQL", "PostgreSQL", "MongoDB", "NoSQL", "SQLite", "Redis",
    "React", "Angular", "Vue", "Node.js", "Express", "Django", "Flask", "FastAPI", "Spring Boot", "ASP.NET",
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Scikit-Learn", "Keras", "NLP",
    "Computer Vision", "Data Science", "Pandas", "NumPy", "Matplotlib", "Tableau",
    "Docker", "Kubernetes", "AWS", "GCP", "Azure", "CI/CD", "Jenkins", "Git", "Terraform", "Ansible",
    "Linux", "Agile", "Scrum", "Kubeflow", "Mlflow", "Cybersecurity", "Penetration Testing"
]

def parse_pdf(path: str) -> str:
    """Helper to extract raw text from PDF."""
    text = ""
    try:
        with open(path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error parsing PDF file: {e}")
    return text

def local_keyword_extraction(text: str):
    """Fallback local extraction using regex/keywords."""
    extracted_skills = []
    text_lower = text.lower()
    
    for skill in TECH_KEYWORDS:
        # Avoid partial word matches (e.g., "Go" in "Google")
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            extracted_skills.append(skill)
            
    # Calculate an ATS score based on length and skill count
    word_count = len(text.split())
    base_score = 40
    
    # Points for word count
    if word_count > 300:
        base_score += 15
    elif word_count > 150:
        base_score += 10
        
    # Points for number of skills matched
    skill_points = min(len(extracted_skills) * 3, 45) # Max 45 points for skills
    ats_score = base_score + skill_points
    
    return {
        "ats_score": min(ats_score, 100),
        "words": word_count,
        "skills_extracted": extracted_skills
    }

def analyze_resume(path: str) -> dict:
    """Resume Parser Agent main function."""
    text = parse_pdf(path)
    if not text:
        return {
            "ats_score": 0,
            "words": 0,
            "skills_extracted": [],
            "error": "Failed to parse PDF text."
        }
        
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if HAS_GEMINI and gemini_key:
        try:
            genai.configure(api_key=gemini_key)
            # Use gemini-1.5-flash as the fast and capable model
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            prompt = f"""
            You are an expert Resume Parser Agent.
            Analyze the following resume text and extract:
            1. An ATS Score (0 to 100) based on professional formatting, structure, and keyword density.
            2. A list of technical skills found in the text.
            
            Return ONLY a valid JSON object matching this structure:
            {{
                "ats_score": 75,
                "skills_extracted": ["Python", "SQL", "Machine Learning"]
            }}
            
            Resume text:
            \"\"\"{text[:4000]}\"\"\"
            """
            
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            data = json.loads(response.text.strip())
            return {
                "ats_score": data.get("ats_score", 50),
                "words": len(text.split()),
                "skills_extracted": data.get("skills_extracted", [])
            }
        except Exception as e:
            print(f"Gemini API parse failed: {e}. Falling back to local rules engine.")
            
    # Fallback to local rule engine if Gemini not present/fails
    return local_keyword_extraction(text)
