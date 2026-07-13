TARGET_SKILLS = {
    "AI Engineer": [
        "Python",
        "SQL",
        "Machine Learning",
        "Deep Learning",
        "TensorFlow",
        "Docker",
        "AWS"
    ]
}

def skill_gap(user_skills):

    required = TARGET_SKILLS["AI Engineer"]

    missing = []

    for skill in required:
        if skill not in user_skills:
            missing.append(skill)

    return {
        "Current Skills": user_skills,
        "Missing Skills": missing
    }