"""
AI Resume Tailor v4.0 - Intelligent Category Detection
Built for Arun's job search - handles with care

Key improvements:
1. Job category detection (RAG, Agentic, FinTech, MLOps, Research)
2. Core Focus Areas section generation
3. Specialist positioning based on detected category
4. Keyword density control (2-4x per critical term)
5. Natural language - no keyword stuffing
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import anthropic
import json
import os
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Resume Tailor", version="4.0")

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


# =============================================================================
# JOB CATEGORY DEFINITIONS
# =============================================================================
# These are the specialist categories that 75% of AI jobs fall into.
# The system will detect which category the job belongs to and position
# Arun as that type of specialist.

JOB_CATEGORIES = """
## JOB CATEGORY DEFINITIONS

You must first analyze the job description and detect which category it falls into.
Most jobs have a PRIMARY category and sometimes a SECONDARY category.

### Category 1: ENTERPRISE_RAG (Document AI / Knowledge Systems)
**Detection signals:**
- Keywords: RAG, retrieval, vector database, semantic search, knowledge base, document, embeddings, Pinecone, ChromaDB, FAISS, Weaviate, search, indexing, knowledge graph, information retrieval, chunking, reranking
- Job focus: Building search systems, document intelligence, knowledge management, internal tools, enterprise search
- Company types: Legal tech, enterprise SaaS, knowledge management, search companies

**When detected, emphasize:**
- Arun's RAG system at Jefferies (30% review time reduction)
- Vector database experience (Pinecone, ChromaDB)
- Document processing at scale
- Semantic search and retrieval quality

### Category 2: AGENTIC_AI (Copilots / Assistants / Multi-Agent Systems)
**Detection signals:**
- Keywords: agent, multi-agent, agentic, copilot, assistant, tool use, tool calling, orchestration, workflow automation, human-in-loop, LangGraph, AutoGen, CrewAI, function calling, ReAct, planning, reasoning, autonomous, MCP, Model Context Protocol
- Job focus: Building AI assistants, automation, decision-making systems, copilots
- Company types: AI-first startups, productivity tools, developer tools

**When detected, MUST emphasize LangGraph (most requested skill in 2025):**
- Arun's multi-agent projects (LLM Code Analyzer, Job Search Assistant)
- LangGraph orchestration for stateful agent workflows
- Tool orchestration and LangChain experience
- Human-in-loop workflows and error recovery
- Task persistence and state management

### Category 3: FINTECH_REGULATED (Financial / Healthcare / Compliance)
**Detection signals:**
- Keywords: financial, fintech, fraud, compliance, risk, regulated, banking, insurance, healthcare, legal, audit, governance, security, sensitive data, PII, HIPAA, SOC2
- Job focus: AI in regulated environments, compliance, risk management, fraud detection
- Company types: Banks, insurance, healthcare, legal tech, fintech

**When detected, emphasize:**
- Arun's Experian fraud detection experience (18% false positive reduction)
- Jefferies financial services background
- Experience with sensitive data and compliance
- Production reliability (98%+ uptime)

### Category 4: MLOPS_PLATFORM (Infrastructure / Deployment / Scaling)
**Detection signals:**
- Keywords: MLOps, deployment, pipeline, infrastructure, scalability, monitoring, CI/CD, Kubernetes, Docker, SageMaker, production, latency, throughput, serving, model registry, observability, vLLM, TensorRT
- Job focus: ML infrastructure, deployment, scaling, platform engineering
- Company types: Large tech, ML platforms, infrastructure companies

**When detected, emphasize:**
- Arun's latency optimization (850ms to 320ms, 62% reduction)
- CI/CD pipelines with GitHub Actions
- AWS SageMaker and Azure ML deployment
- LangSmith and W&B monitoring
- vLLM optimization experience

### Category 5: RESEARCH_FOUNDATION (Research / Fine-tuning / Evaluation)
**Detection signals:**
- Keywords: research, fine-tuning, training, pre-training, RLHF, DPO, evaluation, benchmark, paper, novel, state-of-the-art, PhD, publications, experiments
- Job focus: Model development, research, evaluation frameworks
- Company types: Research labs, foundation model companies

**When detected, emphasize:**
- Arun's model fine-tuning experience
- Evaluation frameworks (LangSmith, W&B)
- Research prototype (Medical Diagnosis Assistant)
- Master's degree + practical experience as PhD alternative
"""


# =============================================================================
# CORE FOCUS AREAS TEMPLATES
# =============================================================================
# These are category-specific keyword sections that go right after the summary.
# They're designed to hit ATS keywords while reading naturally.

CORE_FOCUS_TEMPLATES = """
## CORE FOCUS AREAS SECTION

Based on the detected PRIMARY category, generate a "Core Focus Areas" one-liner.
This section goes RIGHT AFTER the Professional Summary.

CRITICAL FORMAT RULE: Use "|" (pipe) as separator for ATS compatibility
Format: "Core Focus: [phrase] | [phrase] | [phrase] | [phrase] | [phrase] | [phrase]"

### Templates by category (adapt based on specific job keywords):

**ENTERPRISE_RAG:**
Core Focus: Enterprise RAG Systems | Vector Search & Embeddings | Document Intelligence | Semantic Retrieval | LLM Orchestration | Production Knowledge Systems

**AGENTIC_AI:**
Core Focus: LangGraph Agent Orchestration | Multi-Agent Architectures | LLM Tool Integration | AI Copilot Development | Human-in-Loop Workflows | MCP Integration

**FINTECH_REGULATED:**
Core Focus: AI for Regulated Industries | Fraud Detection Systems | Risk Modeling | Compliance-Ready ML Pipelines | Production Financial AI | Data Security

**MLOPS_PLATFORM:**
Core Focus: ML Platform Engineering | Production Model Deployment | Inference Optimization | CI/CD for ML | Scalable AI Infrastructure | Model Observability

**RESEARCH_FOUNDATION:**
Core Focus: LLM Fine-tuning | Model Evaluation Frameworks | Applied AI Research | Experiment Design | Benchmark Development | Research-to-Production

**HYBRID (when multiple categories detected):**
Combine the most relevant phrases from each detected category.
Example for RAG + Agentic: "Core Focus: RAG-Powered Agent Systems | Multi-Agent Orchestration | Vector Search | Tool-Using LLMs | Production AI Copilots | Retrieval Evaluation"
"""


# =============================================================================
# ARUN'S BACKGROUND (Factual - Never modify these facts)
# =============================================================================
ARUN_BACKGROUND = """
## ARUN'S VERIFIED BACKGROUND (These are facts - use them, don't invent new ones)

### Current Role
- Title: AI/ML Engineer (Contract)
- Company: Jefferies Group
- Location: Remote, USA
- Duration: Mar 2024 – Present
- Note: Concurrent with Master's program

### Previous Role
- Title: Associate AI/ML Engineer
- Company: Experian
- Location: Hyderabad, India
- Duration: Jan 2021 – Dec 2022

### Education
- MS Computer Science, Lamar University (Jan 2023 – Dec 2024)
- BTech Computer Science, Sri Indu Institute (Aug 2016 – May 2020)

### Verified Metrics (USE THESE EXACTLY - don't change numbers)
- 30% reduction in manual review time (RAG system at Jefferies)
- 62% latency reduction: 850ms to 320ms (ML inference optimization)
- 18% false positive reduction (fraud detection at Experian)
- 45% API cost reduction (semantic caching in Learning Path Generator)
- 98%+ uptime (production ML models at Experian)
- 15M+ records processed (CLV prediction at Jefferies)
- 25% pipeline efficiency improvement (Azure Data Factory at Experian)

### CRITICAL FORMATTING RULES
- Use "to" instead of arrows (→) to avoid encoding issues in PDFs
- Example: "850ms to 320ms" NOT "850ms → 320ms"
- This prevents character corruption in generated resumes

### Technical Skills (Verified - can reorder but don't add fake skills)
**Programming:** Python, C++, SQL, JavaScript, REST APIs, Git/GitHub, FastAPI, Flask, Streamlit, AsyncIO
**AI/ML Frameworks:** LangChain, LangGraph, LlamaIndex, CrewAI, PyTorch, TensorFlow, Scikit-learn, Hugging Face Transformers, XGBoost, Random Forest, LightGBM
**LLMs & GenAI:** OpenAI GPT, Anthropic Claude Sonnet, Google Gemini, Fine-tuning (LoRA, QLoRA), Prompt Engineering, Groq, Whisper
**Agentic AI:** LangGraph, CrewAI, AutoGen, Multi-Agent Systems, MCP (Model Context Protocol), Tool Orchestration
**MLOps & Cloud:** Docker, Kubernetes, CI/CD, GitHub Actions, AWS (S3, Lambda, SageMaker), Azure (ML, Data Factory), vLLM, Render, Vercel
**Vector Databases:** Pinecone, ChromaDB, FAISS, Azure AI Search, Weaviate
**Data & Analytics:** Pandas, NumPy, SQL, Apache Spark
**Monitoring & Evaluation:** LangSmith, Weights & Biases, MLflow, A/B Testing, Guardrails

### Projects (with actual links - PRESERVE THESE)
1. **LLM Code Analyzer** - Multi-agent code review (GPT-4o, Claude, DeepSeek)
   - GitHub: https://github.com/arunkumar-js25/LLM-Code-Analyzer
   - Demo: https://huggingface.co/spaces/arunkumar-js25/LLM-Code-Analyzer

2. **AI Learning Path Generator** - RAG with ChromaDB/LlamaIndex
   - GitHub: https://github.com/arunkumar-js25/AI_Learning_Path_Generator
   - Demo: https://ai-learning-path-generator.onrender.com

3. **Multimodal Medical Assistant** - PyTorch vision-language models
   - GitHub: https://github.com/arunkumar-js25/Multimodal_Medical_Assistant
   - Demo: https://multimodal-medical-assistant.onrender.com

4. **Job Search Assistant** - Multi-agent FastAPI + Next.js
   - GitHub: https://github.com/arunkumar-js25/JobSearchAssistant
   - Demo: https://job-search-assistant-sigma.vercel.app

### Certifications
- DeepLearning.AI: Generative AI for Everyone, LangChain for LLM Application Development
- Coursera: Machine Learning Specialization (Andrew Ng, Stanford)
"""


# =============================================================================
# KEYWORD DENSITY RULES
# =============================================================================
KEYWORD_RULES = """
## KEYWORD DENSITY RULES (Critical for ATS)

### Frequency Guidelines
- **Primary category keywords:** 3-5 times across entire resume
- **Secondary category keywords:** 2-3 times if applicable
- **Job-specific terms:** 2-4 times each
- **Technical tools mentioned in job:** 2-3 times each

### Distribution Strategy
Keywords should appear NATURALLY across these sections:
1. Professional Summary (1-2 mentions of key terms)
2. Core Focus Areas (concentrated keywords - this is intentional)
3. Technical Skills (tool names)
4. Experience bullets (contextual usage with metrics)
5. Project descriptions (application of skills)

### Anti-Stuffing Rules
- Never use the same keyword more than 5 times total
- Never use a keyword twice in the same sentence
- Never use a keyword twice in the same bullet point
- Keywords must be contextually appropriate
- Read the resume aloud - if it sounds robotic, rewrite it

### Natural Language Priority
The resume must read naturally to a human recruiter AFTER passing ATS.
Keyword optimization is useless if a human rejects it for sounding fake.
"""


# =============================================================================
# MAIN PROMPT BUILDER
# =============================================================================
def build_analysis_prompt(job_description: str, company_name: str, role_title: str) -> str:
    """Build the complete prompt for Claude to analyze and generate tailored content."""
    
    prompt = f"""You are an expert resume strategist specializing in AI/ML engineering roles. Your task is to analyze a job description and generate highly tailored resume content for Arun Kumar Chukkala.

{JOB_CATEGORIES}

{CORE_FOCUS_TEMPLATES}

{ARUN_BACKGROUND}

{KEYWORD_RULES}

---

## JOB TO ANALYZE

**Company:** {company_name}
**Role:** {role_title}

**Job Description:**
{job_description}

---

## YOUR TASK

### Step 1: Category Detection
Analyze the job description and identify:
- PRIMARY category (the main focus of this role)
- SECONDARY category (if applicable)
- Key technical requirements
- Cultural/soft skill signals

### Step 2: Generate Tailored Content
Based on your category detection, generate resume content that positions Arun as a SPECIALIST in what this job needs.

### Step 3: Output Format
Return a JSON object with this EXACT structure:

{{
    "detected_category": {{
        "primary": "ENTERPRISE_RAG | AGENTIC_AI | FINTECH_REGULATED | MLOPS_PLATFORM | RESEARCH_FOUNDATION",
        "secondary": "category or null",
        "confidence": "HIGH | MEDIUM | LOW",
        "reasoning": "1-2 sentences explaining why you chose this category"
    }},
    "core_focus_areas": "Core Focus: [phrase] · [phrase] · [phrase] · [phrase] · [phrase] · [phrase]",
    "summary": "3-4 sentence professional summary positioning Arun as the specialist this job needs. Start with '3+ years of experience' and the specialist title. Include 1-2 key metrics. End with what makes him valuable for THIS specific role.",
    "technical_skills": [
        "Programming & Development: [reorder to put job-critical languages/frameworks FIRST - Python, FastAPI, JavaScript, React if relevant. NEVER add skill levels like (expert) or (proficient)]",
        "AI/ML Frameworks & Tools: [CRITICAL: If job is agentic, start with LangChain, LangGraph, LlamaIndex, CrewAI - these are 2025's most requested skills]",
        "LLMs & Generative AI: [reorder to put job-relevant models/techniques FIRST - OpenAI GPT-4o, Anthropic Claude Sonnet, Google Gemini, Prompt Engineering, Fine-tuning]",
        "Agentic AI & Orchestration: [ONLY if job is agentic - LangGraph, CrewAI, AutoGen, Multi-Agent Systems, MCP, Tool Orchestration]",
        "MLOps & Deployment: [include Docker, Kubernetes if job requires, CI/CD, GitHub Actions, Azure ML, AWS, vLLM]",
        "Data & Vector Databases: [Pinecone, Azure AI Search, ChromaDB, FAISS, Weaviate based on job requirements]",
        "Development Tools & IDEs: Cursor AI, Windsurf AI, VS Code, Jupyter, Linux/Unix",
        "Monitoring & Evaluation: [reorder - LangSmith, Weights & Biases, MLflow, Guardrails, A/B Testing]"
    ],
    "experience_bullets_jefferies": [
        "5 bullets reframed for the detected category",
        "Each bullet: Action verb + what you did + technology used + quantified result",
        "Emphasize the aspects of Jefferies work most relevant to THIS job",
        "Preserve all metrics exactly (30%, 62%, 850ms to 320ms, 15M+)",
        "Use terminology from the job description naturally"
    ],
    "experience_bullets_experian": [
        "4-5 bullets reframed for the detected category",
        "Each bullet: Action verb + what you did + technology used + quantified result",
        "Emphasize aspects most relevant to THIS job",
        "Preserve all metrics exactly (18%, 25%, 98%+)",
        "If job is NOT FinTech focused, still include fraud detection but frame it as 'anomaly detection' or 'ML-based classification'"
    ],
    "project_descriptions": [
        "1-2 sentences for LLM Code Analyzer emphasizing aspects relevant to THIS job. Do NOT start with project name.",
        "1-2 sentences for AI Learning Path Generator emphasizing RAG aspects. Do NOT start with project name.",
        "1-2 sentences for Multimodal Medical Assistant. Do NOT start with project name.",
        "1-2 sentences for Job Search Assistant emphasizing agentic/full-stack aspects. Do NOT start with project name."
    ],
    "keywords_detected": ["list", "of", "15-20", "critical", "keywords", "from", "job", "description"],
    "keyword_usage_plan": {{
        "keyword1": "where and how many times it appears in resume",
        "keyword2": "where and how many times it appears in resume"
    }},
    "title_recommendation": "Recommended title for this application (e.g., 'AI Engineer' or 'RAG Systems Engineer' or 'ML Platform Engineer')"
}}

---

## QUALITY CHECKLIST (Verify before returning)

1. ✅ Category detection is accurate based on job signals
2. ✅ Core Focus Areas matches detected category and job keywords
3. ✅ Summary positions Arun as the specialist THIS job wants
4. ✅ Technical skills are reordered with job priorities FIRST
5. ✅ Experience bullets emphasize category-relevant achievements
6. ✅ All metrics are preserved exactly (30%, 62%, 18%, 45%, 98%+, 15M+, 25%)
7. ✅ All project links will be preserved (handled by frontend)
8. ✅ Keyword density is 2-4x per critical term, distributed naturally
9. ✅ Language is natural, not robotic or keyword-stuffed
10. ✅ A human recruiter would find this compelling, not just ATS

---

## CRITICAL RULES

1. **Never invent experience or metrics** - Use only what's in ARUN'S VERIFIED BACKGROUND
2. **Never remove metrics** - Always include the percentage improvements
3. **Reframe, don't fabricate** - Same experiences, different emphasis based on category
4. **Natural language** - If it sounds like a robot wrote it, rewrite it
5. **Specialist positioning** - Arun should come across as exactly what this job needs
6. **Years of experience** - Use "3+ years" (Jefferies ~1 year + Experian 2 years = ~3 years). Do NOT say 4+ years.
7. **Project descriptions** - Do NOT repeat project name inside the description. BAD: "LLM Code Analyzer: Multi-agent system..." GOOD: "Multi-agent system orchestrating GPT-4o, Claude..."
8. **Docker emphasis** - If job mentions Docker/containerization, mention Docker at least 2-3 times across resume
9. **Latency formatting** - ALWAYS write "850ms to 320ms" NOT "850ms → 320ms" or "850ms->320ms" to avoid encoding issues
10. **LangGraph is CRITICAL** - If job mentions agentic, multi-agent, LangGraph, AutoGen, or CrewAI, ALWAYS include "LangGraph" in AI/ML Frameworks line. This is the #1 requested skill in 2025 AI jobs.
11. **MCP (Model Context Protocol)** - If job mentions tool integration, MCP, or context protocol, include it. It's Anthropic's standard adopted by OpenAI/Google in 2025.
12. **Kubernetes for scale** - If job mentions Kubernetes, k8s, or container orchestration at scale, include in MLOps line
13. **NO SKILL LEVEL TAGS** - NEVER add (expert), (proficient), (advanced), (intermediate) etc. after skills. Just list the skill name. "Python" NOT "Python (expert)". This looks unprofessional and raises expectations.
14. **Core Focus separator** - ALWAYS use "|" (pipe) as separator in Core Focus line, NEVER use "-" or "·". Example: "Core Focus: RAG Systems | LLM Orchestration | Vector Search"

Return ONLY the JSON object. No markdown code blocks. No preamble. No explanation after.
"""
    
    return prompt


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/")
async def read_root():
    """Serve the frontend HTML"""
    index_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "AI Resume Tailor API v4.0", "status": "running"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    return {
        "status": "healthy",
        "version": "4.0",
        "features": ["category_detection", "core_focus_areas", "keyword_density_control"],
        "api_key_configured": bool(api_key),
        "api_key_prefix": api_key[:10] + "..." if api_key else None
    }


@app.post("/api/analyze")
async def analyze_job(request: JobRequest):
    """
    Analyze job description and return tailored content.
    
    This is the main endpoint that:
    1. Detects job category (RAG, Agentic, FinTech, MLOps, Research)
    2. Generates Core Focus Areas section
    3. Creates specialist-positioned resume content
    4. Controls keyword density for ATS optimization
    """
    try:
        # Validate input
        if not request.job_description or len(request.job_description.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Job description is too short. Please provide a complete job description."
            )
        
        # Get API key
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="ANTHROPIC_API_KEY not configured. Please set it in environment variables."
            )
        
        # Initialize Anthropic client
        client = anthropic.Anthropic(api_key=api_key)
        
        # Build the analysis prompt
        prompt = build_analysis_prompt(
            job_description=request.job_description,
            company_name=request.company_name,
            role_title=request.role_title
        )
        
        # Call Claude API
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Extract response content
        content = message.content[0].text.strip()
        
        # Clean JSON response (handle markdown code blocks if present)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        # Parse JSON
        analysis = json.loads(content)
        
        # Validate required fields
        required_fields = [
            "detected_category",
            "core_focus_areas", 
            "summary", 
            "technical_skills", 
            "experience_bullets_jefferies",
            "experience_bullets_experian", 
            "project_descriptions", 
            "keywords_detected"
        ]
        
        missing_fields = [field for field in required_fields if field not in analysis]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Validate detected_category structure
        if "primary" not in analysis.get("detected_category", {}):
            raise ValueError("Missing primary category in detected_category")
        
        # Return successful response
        return {
            "success": True,
            "analysis": analysis,
            "company_name": request.company_name,
            "role_title": request.role_title,
            "version": "4.0"
        }
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {str(e)}")
        print(f"Raw content preview: {content[:500] if 'content' in dir() else 'N/A'}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to parse AI response. Please try again. Error: {str(e)}"
        )
    except anthropic.APIError as e:
        print(f"Anthropic API error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"AI service error: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"Unexpected error: {error_msg}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Server error: {error_msg}"
        )


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "=" * 70)
    print("🚀 AI RESUME TAILOR v4.0 - INTELLIGENT CATEGORY DETECTION")
    print("=" * 70)
    print("\n✅ Features:")
    print("   • Job category detection (RAG, Agentic, FinTech, MLOps, Research)")
    print("   • Core Focus Areas generation")
    print("   • Specialist positioning")
    print("   • Keyword density control")
    print("\n✅ Server starting on http://localhost:8000")
    print("✅ Open your frontend HTML in browser")
    print("\n💡 TIP: Keep this terminal window open")
    print("=" * 70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")