from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import PydanticOutputParser
import os

class JarvisAI:
    """
    Core AI Engine for Jarvis 2.0.
    Manages the interaction with LLMs and processes technical automotive data.
    """
    def __init__(self, output_schema): # <-- ACEPTA EL ESQUEMA PYDANTIC
        self.llm = ChatOpenAI(
            model="gpt-4o", 
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        # 1. Definir el parser y el esquema de salida
        self.parser = PydanticOutputParser(pydantic_object=output_schema)
        
        # 2. Generar el System Prompt completo, incluyendo la instrucción de formato
        self.format_instructions = self.parser.get_format_instructions()

    def get_repair_estimate(self, description: str, context: str = ""):
        """
        Orchestrates logic based on request intent: Financial vs Technical.
        @param description: User query (e.g., 'Estimate in Euros' or 'Mixing ratio').
        """
        system_prompt = (
            "You are Jarvis 2.0, a Senior Collision Adjuster. Your PRIMARY GOAL is to produce a detailed, "
            "itemized cost estimate. Integrate technical data from the 'AXALTA TECHNICAL CONTEXT' to justify material quantities. "
            "Use your professional judgment for typical market rates and labor hours (LOH). "
            "MANDATORY: Follow the EXACT JSON SCHEMA provided below. "
            "The field 'final_technical_verdict' must be highly professional and human. "
            
            f"\n\n--- AXALTA TECHNICAL CONTEXT ---\n{context}"
            f"\n\n--- RESPONSE JSON SCHEMA ---\n{self.format_instructions}" # <-- INSTRUCCIÓN DE FORMATO CRÍTICA
        )
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=description)
        ]
        try:
            # Execute the call to the LLM
            response = self.llm.invoke(messages)
            parsed_data = self.parser.parse(response.content)
            return parsed_data.model_dump_json()
        except Exception as e:
            # Raise exception for the main controller to handle
            raise Exception(f"AI Engine Runtime Error: {str(e)}")