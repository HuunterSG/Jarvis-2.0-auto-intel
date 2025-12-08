from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.engine.ai_engine import JarvisAI
from app.engine.memory_engine import JarvisMemory # Technical memory integration
from dotenv import load_dotenv
from app.engine.finance_engine import FinanceEngine


# Initialize environment variables and engines
load_dotenv()
jarvis = JarvisAI()
memory = JarvisMemory()
finance = FinanceEngine()

# Critical step: Initialize technical knowledge base on server startup
# This scans the /data folder for your Axalta PDFs
memory.process_manuals()

app = FastAPI(
    title="Jarvis 2.0 - Core Engine",
    description="Automotive AI Orchestrator with RAG technical memory",
    version="2.0.0"
)

# Professional-grade data schema for incoming requests
class RepairRequest(BaseModel):
    description: str
@app.on_event("startup")
async def startup_event():
    print("Initializing technical memory in background...")
    memory.process_manuals()
    print("Memory sync complete.")

@app.get("/")
def home():
    """Service status confirmation endpoint."""
    return {"status": "Jarvis 2.0 Online", "mode": "RAG-Enhanced"}

@app.post("/estimate")
async def get_estimate(request: RepairRequest):
    try:
        # Step 1: Detect target currency (default to ARS if not specified)
        target = "ARS" if "ARS" in request.description.upper() else "USD"
        
        # Step 2: Fetch the live market rate
        current_rate = finance.get_real_time_rate(target)
        
        # Step 3: Enhance the query with real financial data
        enhanced_query = (
            f"{request.description}. "
            f"NOTE: Use a strictly updated exchange rate of 1 USD = {current_rate} {target} "
            f"for all financial calculations."
        )
        
        # Step 4: Search manuals and run AI
        technical_context = memory.search_manuals(request.description)
        result = jarvis.get_repair_estimate(enhanced_query, context=technical_context)
        
        return {
            "requested_analysis": request.description,
            "exchange_rate_applied": f"1 USD = {current_rate} {target}",
            "technical_estimate": result,
            "data_source": "Axalta TDS + Live Market Finance"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))