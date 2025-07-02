import os
from typing import Dict, List, Any
import requests

class HybridAI:
    def __init__(self):
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://api.openrouter.ai/v1/"
        if not self.openrouter_api_key:
            raise ValueError("Missing OPENROUTER_API_KEY environment variable")
        self.available = True

    def is_available(self) -> bool:
        return self.available

    def analyze(self, task_type: str, data: str, instructions: str) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
        }

        # Determine model based on task complexity
        complexity = {
            "file_parsing": "google/gemma-2b",
            "profit_analysis": "x/mixtral-8x7b-instruct",
        }.get(task_type, "google/gemma-7b")

        payload = {
            "model": complexity,
            "prompt": f"Instructions: {instructions}\n\nData: {data}",
            "max_tokens": 2048,
            "temperature": 0.1,
        }

        response = requests.post(self.base_url + "completions", json=payload, headers=headers)
        if response.status_code != 200:
            response.raise_for_status()

        result = response.json()
        return {
            "success": True,
            "result": result["choices"][0]["text"].strip(),
            "model_used": payload["model"],
            "cost_estimate": self._estimate_cost(payload["model"], response),
        }

    def _estimate_cost(self, model: str, response: requests.Response) -> Dict[str, float]:
        pricing = {
            "google/gemma-2b": 0.09,
            "google/gemma-7b": 0.35,
            "x/mixtral-8x7b-instruct": 0.32,
        }
        prompt_tokens = response.headers["x-prompt-tokens"]
        completion_tokens = response.headers["x-completion-tokens"]

        input_cost = (int(prompt_tokens) / 1000) * pricing[model]
        output_cost = (int(completion_tokens) / 1000) * pricing[model]
        return {"input_cost": input_cost, "output_cost": output_cost, "total_cost": input_cost + output_cost}

class SmartAnalytics:
    def __init__(self):
        self.ai = HybridAI()

    def analyze_profit_opportunities(self, sales_data: Dict[str, Any], inventory_data: Optional[Dict] = None) -> Dict:
        if not self.ai.is_available():
            return {"success": False, "message": "AI not available. Add OPENROUTER_API_KEY."}

        data_summary = self._summarize_data(sales_data, inventory_data)
        instructions = """
            You are a restaurant profit optimization expert. Perform deep analysis on the provided data to identify:
            - TOP 3 profit leaks
            - Immediate actionable recommendations
            - Profit optimization strategies
            - Price adjustment suggestions
            
            Focus on data-driven insights and specific monetary values. Respond in concise JSON format:
            {"issues": [...], "recommendations": [...]}
        """
        response = self.ai.analyze("profit_analysis", data_summary, instructions)

        if response["success"]:
            try:
                # JSON parse and format results
                raw_response = response["result"]
                insights = {"raw": raw_response}

                # Attempt to parse JSON first
                try:
                    parsed_response = json.loads(raw_response)
                    insights = {
                        "issues": parsed_response.get("issues", []),
                        "recommendations": parsed_response.get("recommendations", []),
                    }
                except:
                    # If not JSON, extract key phrases
                    insights["extractions"] = [
                        line.strip() for line in raw_response.split("\n")
                        if "profit leak" in line.lower() or "recommendation" in line.lower()
                    ]

                # Add cost metadata
                insights["_metadata"] = {
                    "model": response["model_used"],
                    "cost_estimate": response["cost_estimate"]
                }

                return {
                    "success": True,
                    "insights": insights,
                }
            except Exception as e:
                return {"success": False, "error": str(e), "raw": response}

        return response

    def _summarize_data(self, sales_data: Dict[str, Any], inventory_data: Optional[Dict]) -> str:
        summary = f"Sales data count: {len(sales_data)}\n"
        summary += "Total Sales: ${:,.2f}\n".format(sum(sale["amount"] for sale in sales_data))
        summary += "Inventory data count: {} (details excluded for brevity)\n".format(len(inventory_data) if inventory_data else 0)
        return summary
