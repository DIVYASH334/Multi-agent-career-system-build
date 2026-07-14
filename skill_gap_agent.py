import os
import json

# Try to import Gemini SDK
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

# Profile maps containing target skills for key industry roles
ROLE_PROFILES = {
    "AI Engineer": [
        "Python", "SQL", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Docker", "Git"
    ],
    "Fullstack Developer": [
        "JavaScript", "TypeScript", "React", "HTML", "CSS", "Node.js", "Express", "SQL", "Git"
    ],
    "Data Scientist": [
        "Python", "SQL", "Machine Learning", "Pandas", "NumPy", "Tableau", "Data Science", "Git"
    ],
    "DevOps Engineer": [
        "Linux", "Docker", "Kubernetes", "AWS", "CI/CD", "Jenkins", "Git", "Terraform"
    ],
    "Product Manager": [
        "Agile", "Scrum", "SQL", "Tableau", "Git", "Linux"
    ],
    "Cybersecurity Analyst": [
        "Linux", "Python", "Cybersecurity", "Penetration Testing", "SQL", "Git", "Docker"
    ]
}

def analyze_skill_gap(user_skills: list) -> dict:
    """Skill Gap Agent: Evaluates user skills against role profiles."""
    results = {}
    
    # Simple formatting of user skills
    user_skills_clean = [s.strip().lower() for s in user_skills]
    
    for role, required_skills in ROLE_PROFILES.items():
        matching = []
        missing = []
        
        for skill in required_skills:
            if skill.lower() in user_skills_clean:
                matching.append(skill)
            else:
                missing.append(skill)
                
        # Calculate matching percentage
        total_req = len(required_skills)
        match_pct = int((len(matching) / total_req) * 100) if total_req > 0 else 0
        
        results[role] = {
            "match_percentage": match_pct,
            "matching_skills": matching,
            "missing_skills": missing
        }
        
    return results

def get_gemini_skill_guidance(user_skills: list, role: str, missing_skills: list) -> dict:
    """Utilizes Gemini to provide advice on closing the specific skill gap."""
    gemini_key = os.getenv("GEMINI_API_KEY")
    if HAS_GEMINI and gemini_key:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            prompt = f"""
            You are an expert Skill Gap Agent.
            The user wants to become a '{role}'.
            Their current skills: {user_skills}
            Their missing skills: {missing_skills}
            
            Provide a targeted plan (3 action items) to bridge this gap.
            Return ONLY a valid JSON object matching this structure:
            {{
                "learning_path": [
                    "Action 1: Describe courses, resources, or projects",
                    "Action 2: Describe courses, resources, or projects",
                    "Action 3: Describe courses, resources, or projects"
                ]
            }}
            """
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            data = json.loads(response.text.strip())
            return data.get("learning_path", [])
        except Exception as e:
            print(f"Gemini skill gap guidance failed: {e}")
            
    # Default local learning paths based on missing skills
    learning_path = []
    for skill in missing_skills[:3]:
        learning_path.append(f"Learn {skill} through online courses on Udemy/Coursera and build a portfolio project.")
    if not learning_path:
        learning_path.append("Keep updating your portfolio with advanced projects in the target stack.")
    return learning_path
