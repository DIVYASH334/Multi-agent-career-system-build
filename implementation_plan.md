# Multi-Agent Career Recommendation and Guidance System Plan

This project implements a complete, top-to-bottom **Multi-Agent Career Recommendation and Guidance System**. The system consists of a robust **FastAPI backend** running an SQLite database, multiple specialized agents for resume analysis, skill gap assessment, career recommendation, and interview preparation, and a **modern, beautiful React frontend** built with Vite.

The core objective is to allow users to register/login, upload a PDF resume, and receive real-time, high-fidelity AI-driven career path analysis, skill matching, customized technical interview prep, and downloadable PDF roadmap reports.

---

## User Review Required

> [!IMPORTANT]
> The backend agents are designed to connect to the **Google Gemini API** for deep resume parsing and intelligent career matching. If a `GEMINI_API_KEY` is not provided in the environment or fails, the backend will **automatically fall back to a local, regex-based rules engine**. This ensures the application remains fully functional and error-free even in local environments without API key setup.

---

## Open Questions
No open questions at this stage. The system will be built with self-contained, high-quality components and run locally.

---

## Proposed Changes

### Backend Component (FastAPI)
The backend manages API requests, authentication, file uploads, database storage (SQLite), and coordinates agent execution.

#### [NEW] [requirements.txt](file:///c:/Users/divyashree/Downloads/multiagent%20career%20system%20build%20project%20github/backend/requirements.txt)
Defines all Python dependencies including FastAPI, Uvicorn, SQLAlchemy, PyPDF2 for parsing, ReportLab for PDF reports, passlib for password hashing, and google-generativeai.

#### [NEW] [database.py](file:///c:/Users/divyashree/Downloads/multiagent%20career%20system%20build%20project%20github/backend/database.py)
Sets up the SQLite database connection using SQLAlchemy.

#### [NEW] [models.py](file:///c:/Users/divyashree/Downloads/multiagent%20career%20system%20build%20project%20github/backend/models.py)
Defines database tables:
- `User`: User accounts (id, name, email, password_hash)
- `ResumeAnalysis`: Results of parsing (ATS score, extracted skills)
- `CareerRecommendation`: Recommended roles, alignment scores, missing skills, suggested path
- `ChatHistory`: Chat interactions with Career Agents

#### [NEW] [schemas.py](file:///c:/Users/divyashree/Downloads/multiagent%20career%20system%20build%20project%20github/backend/schemas.py)
Pydantic schemas for request and response validation.

#### [NEW] [auth.py](file:///c:/Users/divyashree/Downloads/multiagent%20career%20system%20build%20project%20github/backend/auth.py)
Handles password hashing, token generation (JWT), and route protection.

#### [NEW] [main.py](file:///c:/Users/divyashree/Downloads/multiagent%20career%20system%20build%20project%20github/backend/main.py)
FastAPI application defining routes:
- `/auth/register` and `/auth/login`
- `/resume/upload` (accepts PDF, saves locally, invokes Multi-Agent chain)
- `/career/chat` (allows chat messages with agents)
- `/reports/download` (downloads the PDF report)

#### [NEW] [agents/resume_parser.py](file:///c:/Users/divyashree/Downloads/multiagent%20career%20system%20build%20project%20github/backend/agents/resume_parser.py)
**Resume Parser Agent**: Extracts text from PDF using `PyPDF2`, analyzes word count, and uses Gemini or rule-based matching to list current skills and calculate an ATS score.

#### [NEW] [agents/skill_gap_agent.py](file:///c:/Users/divyashree/Downloads/multiagent%20career%20system%20build%20project%20github/backend/agents/skill_gap_agent.py)
**Skill Gap Agent**: Compares extracted user skills against profiles for major roles (AI Engineer, Fullstack Developer, Data Scientist, DevOps Engineer, Product Manager, Cybersecurity Analyst) to identify matching and missing skills.

#### [NEW] [agents/career_agent.py](file:///c:/Users/divyashree/Downloads/multiagent%20career%20system%20build%20project%20github/backend/agents/career_agent.py)
**Career Recommendation Agent**: Recommends the top matching roles, outlines a step-by-step career path roadmap, and suggests learning resources.

#### [NEW] [agents/interview_agent.py](file:///c:/Users/divyashree/Downloads/multiagent%20career%20system%20build%20project%20github/backend/agents/interview_agent.py)
**Interview Preparation Agent**: Generates typical interview questions and detailed answers customized to the user's missing skills.

#### [NEW] [agents/report_agent.py](file:///c:/Users/divyashree/Downloads/multiagent%20career%20system%20build%20project%20github/backend/agents/report_agent.py)
**Report Agent**: Generates a clean, professional PDF report containing the complete breakdown of the user's career recommendation using `reportlab`.

---

### Frontend Component (React + Vite)
A modern single-page dashboard built with React.

#### [NEW] [package.json](file:///c:/Users/divyashree/Downloads/multiagent%20career%20system%20build%20project%20github/frontend/package.json)
Vite and React setup, configuring scripts.

#### [NEW] [index.html](file:///c:/Users/divyashree/Downloads/multiagent%20career%20system%20build%20project%20github/frontend/index.html)
Initial HTML shell loading Google Fonts (Outfit / Inter).

#### [NEW] [src/main.jsx](file:///c:/Users/divyashree/Downloads/multiagent%20career%20system%20build%20project%20github/frontend/src/main.jsx)
React DOM entry point.

#### [NEW] [src/App.jsx](file:///c:/Users/divyashree/Downloads/multiagent%20career%20system%20build%20project%20github/frontend/src/App.jsx)
React app router/layout, managing auth state and views.

#### [NEW] [src/styles.css](file:///c:/Users/divyashree/Downloads/multiagent%20career%20system%20build%20project%20github/frontend/src/styles.css)
Custom Vanilla CSS implementation featuring:
- Premium glassmorphic cards
- Vibrant purple/indigo/violet gradients
- Fully responsive dashboard layouts
- Custom micro-animations on hover and page load

#### [NEW] [src/components/Login.jsx](file:///c:/Users/divyashree/Downloads/multiagent%20career%20system%20build%20project%20github/frontend/src/components/Login.jsx)
A gorgeous login screen with floating card visuals.

#### [NEW] [src/components/Register.jsx](file:///c:/Users/divyashree/Downloads/multiagent%20career%20system%20build%20project%20github/frontend/src/components/Register.jsx)
Registration screen supporting name, email, and password.

#### [NEW] [src/components/Dashboard.jsx](file:///c:/Users/divyashree/Downloads/multiagent%20career%20system%20build%20project%20github/frontend/src/components/Dashboard.jsx)
The main hub of the application containing several tab views:
- **Overview**: Shows ATS score, skills matched (visualized via a custom animated SVG dial), and basic stats.
- **Skill Gap**: Detail list of current vs. missing skills, with recommended training.
- **Career Pathways**: Displays matching scores for 5 roles and outlines the roadmaps.
- **Interview Prep**: High-quality interactive card-based Q&A tailored to the user's skill gaps.
- **Agent Chat**: A dedicated interface to message the Career Recommendation agent and receive instant advice.
- **Report Exporter**: Downloadable PDF career roadmap button.

---

## Verification Plan

### Automated Tests & Checks
- Verify backend runs properly: `uvicorn main:app --reload --port 8000`
- Verify frontend builds and runs: `npm run dev`
- Upload test resumes and inspect output formats.
- Verify download functionality for the generated report.

### Manual Verification
- Test registration/login flow.
- Test PDF upload with mock content.
- Inspect SVG alignment charts on various viewport widths (responsive check).
- Confirm fallback mechanism triggers if `GEMINI_API_KEY` is not present.
