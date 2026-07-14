import os
import shutil
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import json

# Database & Models
from database import engine, get_db, Base
import models
import schemas
import auth

# Agents
from agents.resume_parser import analyze_resume
from agents.skill_gap_agent import analyze_skill_gap, get_gemini_skill_guidance
from agents.career_agent import generate_roadmap, handle_chat_guidance
from agents.interview_agent import generate_interview_prep
from agents.report_agent import generate_pdf_report

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Multi-Agent Career Recommendation API")

# Configure CORS for local react frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to the frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure uploads directory exists
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ----------------- AUTH ENDPOINTS -----------------

@app.post("/auth/register", response_model=schemas.UserResponse)
def register(user_data: schemas.UserRegister, db: Session = Depends(get_db)):
    # Check if user already exists
    existing = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password and create user
    hashed = auth.get_password_hash(user_data.password)
    db_user = models.User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/auth/login")
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    if not user or not auth.verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "user": {"name": user.name, "email": user.email}}

@app.get("/auth/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

# ----------------- RESUME ENDPOINTS -----------------

@app.post("/resume/upload", response_model=schemas.ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    # Save the PDF to uploads folder
    file_path = os.path.join(UPLOAD_DIR, f"user_{current_user.id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 1. Invoke Resume Parser Agent
    parse_result = analyze_resume(file_path)
    
    # 2. Invoke Skill Gap Agent across all profiles
    gap_results = analyze_skill_gap(parse_result["skills_extracted"])
    
    # Identify the top recommended role (highest matching score)
    top_role = "Fullstack Developer"
    max_match = -1
    for role, analytics in gap_results.items():
        if analytics["match_percentage"] > max_match:
            max_match = analytics["match_percentage"]
            top_role = role
            
    # Get details for the top recommended role
    top_gap = gap_results[top_role]
    missing_skills = top_gap["missing_skills"]
    
    # Get Gemini learning pathway recommendations
    learning_path = get_gemini_skill_guidance(
        user_skills=parse_result["skills_extracted"],
        role=top_role,
        missing_skills=missing_skills
    )
    
    # 3. Invoke Career Agent to generate milestone roadmap
    roadmap = generate_roadmap(top_role, missing_skills)
    
    # Write to database (Resume Analysis)
    db_analysis = models.ResumeAnalysis(
        user_id=current_user.id,
        filename=file.filename,
        ats_score=parse_result["ats_score"],
        words=parse_result["words"],
        skills_extracted=", ".join(parse_result["skills_extracted"])
    )
    db.add(db_analysis)
    
    # Write to database (Career Recommendation)
    db_rec = models.CareerRecommendation(
        user_id=current_user.id,
        recommended_role=top_role,
        match_percentage=max_match,
        missing_skills=", ".join(missing_skills),
        learning_path=json.dumps(learning_path),
        roadmap=roadmap
    )
    db.add(db_rec)
    db.commit()
    
    return {
        "ats_score": parse_result["ats_score"],
        "words": parse_result["words"],
        "skills_extracted": parse_result["skills_extracted"],
        "career_recommendation": {
            "recommended_role": top_role,
            "match_percentage": max_match,
            "missing_skills": missing_skills,
            "learning_path": learning_path,
            "roadmap": roadmap
        }
    }

@app.get("/resume/latest")
def get_latest_analysis(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    analysis = db.query(models.ResumeAnalysis).filter(
        models.ResumeAnalysis.user_id == current_user.id
    ).order_by(models.ResumeAnalysis.created_at.desc()).first()
    
    rec = db.query(models.CareerRecommendation).filter(
        models.CareerRecommendation.user_id == current_user.id
    ).order_by(models.CareerRecommendation.created_at.desc()).first()
    
    if not analysis or not rec:
        raise HTTPException(status_code=404, detail="No resume uploaded yet.")
        
    try:
        learning_path = json.loads(rec.learning_path)
    except:
        learning_path = [step.strip() for step in rec.learning_path.split('\n') if step]
        
    skills = [s.strip() for s in analysis.skills_extracted.split(',') if s.strip()]
    missing = [s.strip() for s in rec.missing_skills.split(',') if s.strip()]
    
    return {
        "ats_score": analysis.ats_score,
        "words": analysis.words,
        "skills_extracted": skills,
        "career_recommendation": {
            "recommended_role": rec.recommended_role,
            "match_percentage": rec.match_percentage,
            "missing_skills": missing,
            "learning_path": learning_path,
            "roadmap": rec.roadmap
        }
    }

# ----------------- CHAT ENDPOINTS -----------------

@app.post("/career/chat", response_model=schemas.ChatResponse)
def chat_with_advisor(
    request: schemas.ChatRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Save User message
    user_msg = models.ChatHistory(
        user_id=current_user.id,
        sender="user",
        message=request.message
    )
    db.add(user_msg)
    db.commit()
    
    # Retrieve past messages
    history_records = db.query(models.ChatHistory).filter(
        models.ChatHistory.user_id == current_user.id
    ).order_by(models.ChatHistory.timestamp.asc()).all()
    
    history_list = [
        {"sender": r.sender, "message": r.message} for r in history_records
    ]
    
    # 4. Invoke Career Agent (Advisor) Chat responder
    response_text = handle_chat_guidance(request.message, history_list)
    
    # Save Agent Response
    agent_msg = models.ChatHistory(
        user_id=current_user.id,
        sender="advisor",
        message=response_text
    )
    db.add(agent_msg)
    db.commit()
    db.refresh(agent_msg)
    
    return agent_msg

@app.get("/career/chat/history", response_model=List[schemas.ChatResponse])
def get_chat_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    chats = db.query(models.ChatHistory).filter(
        models.ChatHistory.user_id == current_user.id
    ).order_by(models.ChatHistory.timestamp.asc()).all()
    return chats

# ----------------- PREP & REPORT ENDPOINTS -----------------

@app.get("/career/interview-prep")
def get_interview_questions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Get latest recommendation
    rec = db.query(models.CareerRecommendation).filter(
        models.CareerRecommendation.user_id == current_user.id
    ).order_by(models.CareerRecommendation.created_at.desc()).first()
    
    if not rec:
        raise HTTPException(status_code=404, detail="Upload your resume first to generate custom interview questions.")
        
    missing = [s.strip() for s in rec.missing_skills.split(',') if s.strip()]
    
    # 5. Invoke Interview Prep Agent
    qna_list = generate_interview_prep(rec.recommended_role, missing)
    return qna_list

@app.get("/reports/download")
def download_pdf_report(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Fetch latest recommendations
    analysis = db.query(models.ResumeAnalysis).filter(
        models.ResumeAnalysis.user_id == current_user.id
    ).order_by(models.ResumeAnalysis.created_at.desc()).first()
    
    rec = db.query(models.CareerRecommendation).filter(
        models.CareerRecommendation.user_id == current_user.id
    ).order_by(models.CareerRecommendation.created_at.desc()).first()
    
    if not analysis or not rec:
        raise HTTPException(status_code=404, detail="Analyze your resume first to download the report.")
        
    try:
        learning_path = json.loads(rec.learning_path)
    except:
        learning_path = [step.strip() for step in rec.learning_path.split('\n') if step]
        
    skills = [s.strip() for s in analysis.skills_extracted.split(',') if s.strip()]
    missing = [s.strip() for s in rec.missing_skills.split(',') if s.strip()]
    
    # Get Interview Questions for PDF
    qna_list = generate_interview_prep(rec.recommended_role, missing)
    
    # Generate temporary PDF filename
    pdf_filename = f"report_user_{current_user.id}.pdf"
    
    # 6. Invoke Report Agent
    success = generate_pdf_report(
        filename=pdf_filename,
        user_name=current_user.name,
        ats_score=analysis.ats_score,
        skills=skills,
        role=rec.recommended_role,
        match_pct=rec.match_percentage,
        missing=missing,
        learning_path=learning_path,
        roadmap_text=rec.roadmap,
        interview_prep=qna_list
    )
    
    if not success or not os.path.exists(pdf_filename):
        raise HTTPException(status_code=500, detail="Failed to generate PDF report.")
        
    return FileResponse(
        path=pdf_filename,
        filename="Career_Roadmap_Report.pdf",
        media_type="application/pdf"
    )

# Mount static folder and serve frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h3>static/index.html not found. Make sure it is created in backend/static/index.html.</h3>"

