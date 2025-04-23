import google.generativeai as genai
import os

def initialize_gemini(api_key):
    """Initialize the Gemini API with the provided API key."""
    genai.configure(api_key=api_key)

def convert_currency(api_key, amount, from_currency, to_currency):
    """Convert currency using Gemini AI API."""
    initialize_gemini(api_key)

    prompt = (f"Convert {amount} {from_currency} to {to_currency}. "
              "Provide the most accurate exchange rate and converted amount.")
    
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text  # Extracting the AI-generated response

if __name__ == "__main__":
    API_KEY = "AIzaSyCfzJ_B-5Dv7LukfPcxr4urmNzzz4VqPGA"  # Replace with your actual API key
    amount = float(input("Enter amount: "))
    from_currency = input("Enter from currency (e.g., USD): ").upper()
    to_currency = input("Enter to currency (e.g., INR): ").upper()
    
    result = convert_currency(API_KEY, amount, from_currency, to_currency)
    print("Conversion Result:", result)