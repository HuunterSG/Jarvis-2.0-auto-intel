from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import os

class JarvisAI:
    """
    Core AI Engine for Jarvis 2.0.
    Manages the interaction with LLMs and processes technical automotive data.
    """
    def __init__(self):
        # Initialize the model using secure environment variables
        self.llm = ChatOpenAI(
            model="gpt-4o", 
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

    def get_repair_estimate(self, description: str, context: str = ""):
        """
        Orchestrates logic based on request intent: Financial vs Technical.
        @param description: User query (e.g., 'Estimate in Euros' or 'Mixing ratio').
        """
        messages = [
            SystemMessage(content=(
                "You are Jarvis 2.0. You must handle two types of requests:\n"
                "1. FINANCIAL: If the user asks for costs, you MUST calculate them and convert them "
                "strictly to the requested currency using current approximate exchange rates.\n"
                "2. TECHNICAL: If the user asks for procedures, base your answer strictly on the "
                "provided Axalta context.\n"
                "MANDATORY: Always specify which exchange rate you used if a conversion was made."
                f"\n\n--- AXALTA TECHNICAL DATA ---\n{context}"
            )),
            HumanMessage(content=description)
        ]
        try:
            # Execute the call to the LLM
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            # Raise exception for the main controller to handle
            raise Exception(f"AI Engine Runtime Error: {str(e)}")