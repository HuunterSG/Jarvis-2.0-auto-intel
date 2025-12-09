from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.engine.ai_engine import JarvisAI
from app.engine.memory_engine import JarvisMemory # Technical memory integration
from dotenv import load_dotenv
from app.engine.finance_engine import FinanceEngine
from pydantic import BaseModel, Field
import json

class CostItem(BaseModel):
    """Modelo para un ítem desglosado en el presupuesto."""
    description: str = Field(description="Descripción del costo (e.g., Imprimación, Capa Base, Mano de Obra).")
    usd_per_unit: float = Field(description="Costo unitario en USD.")
    quantity: float = Field(description="Cantidad requerida (litros o horas).")
    cost_ars: float = Field(description="Costo total de esta línea ya convertido a ARS.")

class EstimateOutput(BaseModel):
    """Modelo de salida estructurada para el presupuesto final."""
    final_technical_verdict: str = Field(description="Un resumen inicial, profesional y persuasivo del perito. Debe ser humano y justificar el presupuesto.")
    material_costs: list[CostItem] = Field(description="Lista de costos desglosados para materiales (pintura, barniz, etc.).")
    labor_and_oh_costs: list[CostItem] = Field(description="Lista de costos desglosados para mano de obra (LOH) y gastos operativos.")
    evidence_source: str = Field(description="Nombre del documento técnico de Axalta usado como evidencia.")
    total_ars: float = Field(description="El costo total general final en ARS.")
    exchange_rate: float = Field(description="El tipo de cambio aplicado (e.g., 1438.58).")




# Initialize environment variables and engines
load_dotenv()
jarvis = JarvisAI(output_schema=EstimateOutput)
ai_engine = JarvisAI(output_schema=EstimateOutput)
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
    # Usamos async para manejar operaciones I/O como las llamadas a la API
    try:
        # Step 1: Detect target currency (default to ARS if not specified)
        # Y aseguramos que siempre sea una de las monedas que queremos usar
        target = "ARS" if "ARS" in request.description.upper() else "USD"
        
        # Step 2: Fetch the live market rate (Asumiendo que 'finance' es tu módulo finance_engine)
        # Esto es crucial para la credibilidad financiera.
        current_rate = finance.get_real_time_rate(target)
        
        # Step 3: Enhance the query with real financial data
        enhanced_query = (
            f"{request.description}. "
            f"NOTE: Use a strictly updated exchange rate of 1 USD = {current_rate} {target} "
            f"for all financial calculations."
        )
        
        # Step 4: Search manuals (RAG)
        technical_context, data_sources = memory.search_manuals(request.description)
        
        # Step 5: Generación del Presupuesto (La IA devuelve un string JSON)
        # El AI Engine usará el contexto técnico y el tipo de cambio real para llenar el JSON.
        json_estimate_str = ai_engine.get_repair_estimate(
            description=enhanced_query,
            context=technical_context
        )
        
        # Step 6: Parsear el JSON de la IA para devolver un objeto limpio
        # Usamos json.loads() para convertir la cadena JSON en un diccionario Python.
        final_data = json.loads(json_estimate_str)
        
        # Step 7: Añadir metadatos de la aplicación (fuentes y tipo de cambio)
        # El LLM ya incluyó estos datos, pero los sobrescribimos para asegurar la fuente más fidedigna.
        final_data['evidence_source'] = data_sources
        final_data['exchange_rate'] = current_rate
        
        # Devolvemos el diccionario JSON completo, listo para Streamlit
        return final_data

    except Exception as e:
        # Esto capturará fallos de la IA (JSON inválido) o fallos de la API financiera.
        print(f"FATAL ERROR IN ESTIMATE ENDPOINT: {e}")
        raise HTTPException(status_code=500, detail=f"AI/RAG Processing Error: {str(e)}")