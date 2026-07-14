import os
import json

# Try to import Gemini SDK
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

# Default Roadmaps for fallback
DEFAULT_ROADMAPS = {
    "AI Engineer": """### AI Engineer Career Roadmap

1. **Foundations (Month 1-2)**:
   - Deepen your core Python knowledge (oop, generators, testing).
   - Solidify SQL databases and data retrieval strategies.
   
2. **Core ML / Deep Learning (Month 3-4)**:
   - Study Scikit-Learn, Pandas, and NumPy for classical machine learning.
   - Progress to deep learning frameworks (PyTorch or TensorFlow) for neural networks.
   
3. **Advanced AI & MLOps (Month 5-6)**:
   - Build and scale models using Mlflow or Kubeflow.
   - Containerize workloads with Docker and deploy to AWS/GCP pipelines.
   - Build a portfolio containing an end-to-end LLM application.""",

    "Fullstack Developer": """### Fullstack Developer Career Roadmap

1. **Advanced Frontend (Month 1-2)**:
   - Master React.js hooks, routing, and modern state management (Zustand or Redux).
   - Improve CSS layout design using flexbox, grid, and CSS custom properties.
   
2. **Backend Architecture (Month 3-4)**:
   - Master Node.js & Express or FastAPI for designing robust, secure API routes.
   - Implement relational and non-relational database schemas (PostgreSQL, MongoDB).
   
3. **Deployment & Operations (Month 5-6)**:
   - Learn Docker containerization and host servers on GCP/AWS/Render.
   - Set up CI/CD workflows using Git and GitHub Actions.
   - Build a fully responsive web application from backend schemas to front-end CSS.""",

    "Data Scientist": """### Data Scientist Career Roadmap

1. **Statistical Analysis & Python (Month 1-2)**:
   - Deep dive into probability, regression, and data wrangling with Pandas/NumPy.
   
2. **Machine Learning & Modeling (Month 3-4)**:
   - Train classification, clustering, and regression models in Scikit-Learn.
   - Focus on feature engineering, validation, and performance metrics.
   
3. **Storytelling & Visualization (Month 5-6)**:
   - Learn visualization tools like Tableau or PowerBI.
   - Master telling stories with data, preparing business slide decks.
   - Deploy interactive dashboards using Streamlit or React.""",

    "DevOps Engineer": """### DevOps Engineer Career Roadmap

1. **Linux Systems & Git (Month 1-2)**:
   - Master command-line utilities, script automation, and Git hooks.
   
2. **Containerization & CI/CD (Month 3-4)**:
   - Learn Docker inside out. Move to Kubernetes for cluster orchestration.
   - Implement CI/CD pipelines (Jenkins, GitHub Actions, GitLab CI).
   
3. **Infrastructure as Code (Month 5-6)**:
   - Learn Terraform to declare infrastructure on AWS/Azure.
   - Build configuration scripts using Ansible.
   - Set up logging, alerting, and telemetry dashboards (Prometheus, Grafana).""",

    "Product Manager": """### Product Manager Career Roadmap

1. **Product Fundamentals (Month 1-2)**:
   - Study product lifecycle, user persona research, and KPI definitions.
   
2. **Agile Methodologies & Tools (Month 3-4)**:
   - Master Jira, Confluence, and the Scrum framework.
   - Learn SQL and data analytics (Tableau) to support data-informed product decisions.
   
3. **Strategy & Launch (Month 5-6)**:
   - Learn wireframing, roadmap prioritization (RICE framework), and GTM strategy.
   - Lead a practice cohort project to launch a mock application.""",

    "Cybersecurity Analyst": """### Cybersecurity Analyst Career Roadmap

1. **Networking & Operating Systems (Month 1-2)**:
   - Learn network protocols (TCP/IP, DNS, VPNs) and Linux administration.
   
2. **Defensive & Offensive Security (Month 3-4)**:
   - Study ethical hacking, penetration testing tools, and vulnerability assessment.
   - Understand cryptography algorithms, SSL/TLS, and secure design patterns.
   
3. **SIEM & Response (Month 5-6)**:
   - Learn to monitor and respond using SIEM tools.
   - Secure server environments with Docker and network firewalls.
   - Prepare for security certifications (CompTIA Security+, CEH)."""
}

def generate_roadmap(role: str, missing_skills: list) -> str:
    """Generates a detailed roadmap for the chosen career role."""
    gemini_key = os.getenv("GEMINI_API_KEY")
    if HAS_GEMINI and gemini_key:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            prompt = f"""
            You are an expert Career Recommendation Agent.
            The user is aiming to become a '{role}'.
            They are missing the following skills: {missing_skills}
            
            Generate a detailed, step-by-step career path roadmap showing months and actionable steps.
            Write it in clean markdown layout.
            """
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini roadmap generation failed: {e}")
            
    return DEFAULT_ROADMAPS.get(role, DEFAULT_ROADMAPS["AI Engineer"])

def handle_chat_guidance(user_message: str, chat_history: list) -> str:
    """Handles conversational career guidance using Gemini or fallback."""
    gemini_key = os.getenv("GEMINI_API_KEY")
    if HAS_GEMINI and gemini_key:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            # Format history for prompt
            formatted_history = ""
            for chat in chat_history[-6:]:
                formatted_history += f"{chat['sender']}: {chat['message']}\n"
                
            prompt = f"""
            You are a helpful, professional AI Career Advisor.
            You help students and professionals plan their careers, upgrade their skills, and practice interviews.
            
            Recent Chat History:
            {formatted_history}
            
            User: {user_message}
            Advisor:
            """
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini career agent chat failed: {e}")
            
    # Simple Fallback chatbot responses
    msg = user_message.lower()
    if "skills" in msg or "skill" in msg:
        return "To improve your skills, look at your Skill Gap tab. We have identified key missing skills like Docker, Cloud platforms, and Advanced Python. Taking targeted courses on Udemy or Coursera is a great start."
    elif "interview" in msg:
        return "Preparing for interviews requires a solid grasp of core technical questions. Check out the 'Interview Prep' tab in your dashboard where our agent generated customized Q&As based on your resume!"
    elif "resume" in msg or "ats" in msg:
        return "To improve your ATS score, make sure to add specific keywords matching the jobs you apply to, keep the PDF structure single-column, and avoid text boxes or graphics."
    elif "hello" in msg or "hi" in msg:
        return "Hello! I am your AI Career Advisor. Ask me anything about job roles, resumes, interview preparation, or learning roadmaps!"
    else:
        return "That's a great question. Developing a strong portfolio of projects and studying the core concepts of your chosen tech stack is key to career growth. Feel free to ask more specific questions!"
