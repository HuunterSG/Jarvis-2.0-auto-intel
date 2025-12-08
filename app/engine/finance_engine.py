import requests
import os
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

class FinanceEngine:
    """
    Handles real-time financial data retrieval for Jarvis 2.0.
    """
    def __init__(self):
        # We use ExchangeRate-API (Free tier)
        self.api_key = os.getenv("EXCHANGERATE_API_KEY")
        self.base_url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/latest/USD"

    def get_real_time_rate(self, target_currency: str = "ARS"):
        """
        Fetches the current exchange rate from USD to the target currency.
        @param target_currency: The ISO code of the currency (ARS, EUR, MXN).
        """
        try:
            # External API call to fetch market rates
            response = requests.get(self.base_url, timeout=5)
            data = response.json()
            
            if response.status_code == 200 and data['result'] == 'success':
                # Extract the specific conversion rate
                rate = data['conversion_rates'].get(target_currency, 1100.0)
                return rate
            return 1100.0  # Professional fallback in case of API downtime
        except Exception as e:
            # Log error and return a safe fallback value
            print(f"Finance Engine Error: {str(e)}")
            return 1100.0