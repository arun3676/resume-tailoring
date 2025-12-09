"""
AI Resume Tailor - Production Backend Server
Optimized for Render.com deployment
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import anthropic
import json
import os
import traceback
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="AI Resume Tailor", version="2.1")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class JobRequest(BaseModel):
    job_description: str
    company_name: str = "Company"
    role_title: str = "AI_Engineer"

# Serve static files (frontend)
@app.get("/")
async def read_root():
    """Serve the frontend HTML"""
    index_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "AI Resume Tailor API", "status": "running"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    return {
        "status": "healthy",
        "api_key_configured": bool(api_key),
        "api_key_prefix": api_key[:10] + "..." if api_key else None
    }

@app.post("/api/analyze")
async def analyze_job(request: JobRequest):
    """Analyze job description and return tailored content"""
    try:
        # Get API key from environment variable
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500, 
                detail="ANTHROPIC_API_KEY not configured. Please set it in Render environment variables."
            )
        
        client = anthropic.Anthropic(api_key=api_key)
        
        prompt = f"""You are an expert resume writer and ATS optimization specialist. Analyze this job description and generate tailored resume content for Arun Kumar Chukkala.

CANDIDATE BACKGROUND:
- Current Role: AI/ML Engineer (Contract) at Jefferies Group, Remote USA (Mar 2024-Present, concurrent with Master's)
- Previous Role: Associate AI/ML Engineer at Experian, Hyderabad India (Jan 2021-Dec 2022)
- Education: MS Computer Science, Lamar University (2023-2024); BTech CS (2016-2020)
- Programming: Python (expert), C++ (proficient), SQL, JavaScript
- Core Expertise: PyTorch, TensorFlow, production LLM applications, RAG systems, multi-agent workflows, automated testing
- Management Experience: Worked with 10 direct reports at Jefferies, collaborated with cross-functional teams, mentored junior engineers
- Key Achievements: 30% review time reduction, 62% latency improvement (850ms→320ms using PyTorch optimization), 18% false positive reduction, 45% API cost reduction, 98%+ uptime, 15M+ records processed, 25% efficiency gain

CORE PROJECTS:
1. LLM Code Analyzer: Multi-agent code review (GPT-4o, Claude, DeepSeek), LangSmith observability, automated testing, Streamlit on Hugging Face
2. AI Learning Path Generator: RAG with ChromaDB/LlamaIndex, statistical optimization, CI/CD on Render  
3. Multimodal Medical Assistant: PyTorch vision-language models for X-ray analysis, Whisper audio, Flask+Docker, quality workflows
4. Job Search Assistant: FastAPI+Next.js multi-agent platform with automated testing, Vercel+Render deployment

JOB DESCRIPTION:
{request.job_description}

COMPANY: {request.company_name}
ROLE: {request.role_title}

Generate tailored resume JSON focusing on THIS SPECIFIC JOB:
{{
    "summary": "3-4 sentences emphasizing MOST RELEVANT experience to THIS job. Focus on what THIS role needs most.",
    "technical_skills": [
        "Programming & Development: Python, C++, SQL, JavaScript, REST APIs, Git/GitHub, FastAPI, Flask, Streamlit, AsyncIO",
        "AI/ML Frameworks & Tools: PyTorch, TensorFlow, Scikit-learn, Hugging Face Transformers, LangChain, LlamaIndex, XGBoost",
        "LLMs & Generative AI: OpenAI GPT-4o/GPT-5, Anthropic Claude Sonnet 4.5, Google Gemini 2.5 Pro, AI Model Fine-tuning, Prompt Engineering, Groq, Whisper",
        "MLOps & Deployment: Docker, CI/CD Pipelines, GitHub Actions, AWS (S3, Lambda, SageMaker), Azure (ML, Data Factory), vLLM, Render, Vercel, Automated Testing",
        "Data & Vector Databases: RAG Systems, Pinecone, ChromaDB, FAISS, Large-scale Datasets, Semantic Search, Pandas, NumPy, SQL Databases",
        "Development Tools & IDEs: Cursor AI, Windsurf AI, VS Code, Jupyter, Linux/Unix",
        "Monitoring & Evaluation: LangSmith, Weights & Biases, MLflow, Statistical Analysis, Model Performance Tracking, A/B Testing, Quality Metrics"
    ],
    "experience_bullets_jefferies": [
        "Designed RAG-based document retrieval with LangChain and Pinecone, reducing manual review time by 30%",
        "Optimized ML inference using PyTorch and vLLM, achieving 62% latency reduction from 850ms to 320ms",
        "Developed customer lifetime value prediction models on 15M+ record datasets using Python and AWS SageMaker",
        "Implemented automated model evaluation workflows using LangSmith and Weights & Biases for quality tracking",
        "Built CI/CD pipelines with GitHub Actions for automated ML model deployment and testing"
    ],
    "experience_bullets_experian": [
        "Developed ML-based fraud detection using PyTorch Isolation Forest and Autoencoders, reducing false positives by 18%",
        "Designed Azure Data Factory pipelines for large-scale dataset processing, improving efficiency by 25%",
        "Deployed production ML models to Azure ML platform, maintaining 98%+ uptime through robust monitoring",
        "Created Power BI dashboards for model performance tracking and cross-functional quality reporting",
        "Collaborated with 10+ cross-functional team members implementing data-driven quality improvements"
    ],
    "project_descriptions": [
        "Multi-agent code review platform using GPT-4o, Claude, and DeepSeek with LangSmith observability for automated quality assessment, deployed on Hugging Face Spaces with Streamlit",
        "RAG-based learning path generator with ChromaDB and LlamaIndex, implementing statistical optimization to reduce API costs by 45%, deployed on Render with CI/CD pipelines",
        "PyTorch vision-language model for automated medical image analysis with Whisper audio integration, deployed via Docker for scalable quality workflows",
        "Multi-agent FastAPI+Next.js platform for autonomous decision-making with automated testing and cross-functional workflow optimization, deployed on Vercel+Render"
    ],
    "keywords": ["15-20 critical keywords from job description"],
    "role_focus": "1 sentence describing what THIS specific role prioritizes most"
}}

CRITICAL TAILORING RULES FOR THIS JOB:
1. **Match job priorities exactly**: If job emphasizes PyTorch → feature it prominently. If quality/testing → emphasize that. Don't use generic framing.
2. **Keyword frequency limits**: 
   - Any single term: 2-4 times MAX across entire resume
   - "Agentic/agent": 3-4 times MAX (only if job mentions it 2+times)
   - "PyTorch": 3-5 times if mentioned in requirements
   - "Quality/QA": 4-6 times if job is QA-focused
   - "Testing": 3-5 times if automated testing is key
3. **Preserve ALL metrics**: 30%, 62%, 850ms→320ms, 18%, 45%, 98%+, 15M+, 25%
4. **Experience bullet strategy**:
   - Start with action verbs: Designed, Engineered, Developed, Built, Implemented, Optimized, Architected
   - Reframe SAME achievements to match THIS job's focus
   - Jefferies: 5 bullets emphasizing what THIS job needs most
   - Experian: 4-5 bullets emphasizing what THIS job needs most
5. **Technical skills**: Reorder tools within each category to put job-critical tech FIRST in each list
6. **PhD preference**: If job prefers PhD, emphasize Master's + 3 years experience + research-oriented projects
7. **C++ requirement**: If job requires C++, mention in skills AND add to at least one experience bullet
8. **Cross-functional collaboration**: If mentioned in job, emphasize teamwork, mentoring, communication in bullets
9. **Natural language**: Write like a human. Vary vocabulary. Don't stuff keywords robotically.
10. **Project descriptions**: 1-2 sentences highlighting technologies mentioned in THIS job description

QUALITY CHECK BEFORE RETURNING:
- Does summary directly address THIS job's main focus?
- Are technical skills ordered with THIS job's priorities first?
- Do experience bullets emphasize what THIS job cares about most?
- Is keyword usage natural (not repetitive/robotic)?
- Are all metrics preserved?
- Will this pass ATS for THIS specific job?

Return ONLY valid JSON - no markdown, no code blocks, no preamble:"""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = message.content[0].text.strip()
        
        # Clean JSON response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        analysis = json.loads(content)
        
        # Validate response structure
        required_fields = ["summary", "technical_skills", "experience_bullets_jefferies", 
                          "experience_bullets_experian", "project_descriptions", "keywords"]
        for field in required_fields:
            if field not in analysis:
                raise ValueError(f"Missing required field: {field}")
        
        return {
            "success": True,
            "analysis": analysis,
            "company_name": request.company_name,
            "role_title": request.role_title
        }
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {str(e)}")
        print(f"Raw content: {content[:500] if 'content' in dir() else 'N/A'}")
        raise HTTPException(status_code=500, detail=f"JSON parsing error: {str(e)}")
    except anthropic.APIError as e:
        print(f"Anthropic API error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Anthropic API error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Server error: {type(e).__name__}: {str(e)}"
        print(f"Exception: {error_msg}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg)

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 AI RESUME TAILOR - BACKEND SERVER v2.1")
    print("="*60)
    print("\n✅ Server starting on http://localhost:8000")
    print("✅ Open AI_Resume_Tailor_App.html in your browser")
    print("\n💡 TIP: Keep this terminal window open")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
