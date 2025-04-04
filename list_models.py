import google.generativeai as genai

# Configure the Gemini API
genai.configure(api_key="AIzaSyBHsQiaVTGtu6YFQFXxdu08my5QuKUK6yQ")

# List available models
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"Model: {m.name}")
        print(f"Supported methods: {m.supported_generation_methods}")
        print("---") 