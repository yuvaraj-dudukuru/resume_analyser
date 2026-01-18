import google.generativeai as genai
import os

def list_models():
    api_key = input("Enter your Google API Key: ").strip()
    if not api_key:
        print("No API key entered.")
        return

    try:
        genai.configure(api_key=api_key)
        print("\nChecking available models...")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_models()
