import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

class FinanceLLMReasoner:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("WARNING: GEMINI_API_KEY not found in .env file!")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name='gemini-3.6-flash',
            system_instruction="You are an expert AI Finance Controller. Your job is to review transaction exceptions and provide a 1-sentence plain-English explanation, followed by a 1-sentence recommended action for the finance team. Be concise and professional."
        )

    def analyze_exception(self, exception_data: dict) -> dict:
        """
        Takes a raw exception from the Reconciler Engine and asks Gemini to explain it.
        """
        prompt = f"""
        Analyze this reconciliation exception:
        Order ID: {exception_data.get('order_id')}
        Expected Amount: {exception_data.get('expected_amount')}
        Settled Amount: {exception_data.get('actual_settled_amount')}
        Discrepancy: {exception_data.get('discrepancy')}
        System Status: {exception_data.get('status')}
        System Reason: {exception_data.get('reason')}

        Return your analysis exactly in this format:
        AI Reasoning: [Your explanation of what likely happened based on the amounts and status]
        Recommended Action: [What the human accountant should do next]
        """
        
        try:
            response = self.model.generate_content(prompt)
            lines = response.text.strip().split('\n')
            
            ai_reasoning = "Could not parse reasoning."
            ai_action = "Manual review required."
            
            for line in lines:
                if line.startswith("AI Reasoning:"):
                    ai_reasoning = line.replace("AI Reasoning:", "").strip()
                elif line.startswith("Recommended Action:"):
                    ai_action = line.replace("Recommended Action:", "").strip()
                    
            return {
                "ai_reasoning": ai_reasoning,
                "ai_action": ai_action
            }
            
        except Exception as e:
            return {
                "ai_reasoning": f"AI Engine Offline: {str(e)}",
                "ai_action": "Proceed with standard manual review."
            }