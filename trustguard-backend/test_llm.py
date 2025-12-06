import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_llm_connection():
    print("Testing LLM Connection...")
    
    # Get configuration
    api_key = os.getenv("LLM_API_KEY", "")
    if not api_key or api_key == "dummy":
        print("⚠️ WARNING: LLM_API_KEY is missing or set to 'dummy'. Nvidia Cloud API requires a valid key.")
        
    # Nvidia NIM Cloud API
    urls = [
        "https://integrate.api.nvidia.com/v1/chat/completions"
    ]
    
    # Common Nvidia NIM models to try
    models = [
        "meta/llama3-8b-instruct",
        "meta/llama3-70b-instruct",
        "nvidia/llama-3.1-nemotron-70b-instruct",
        "mistralai/mixtral-8x7b-instruct-v0.1"
    ]
    
    for model in models:
        print(f"\nTesting Model: {model}")
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "hello"}],
            "max_tokens": 10
        }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    success = False
    
    for url in urls:
        print(f"\nTrying URL: {url}")
        try:
            # Adjust payload for Ollama if needed, but standard OpenAI format is usually supported
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                print("Response:")
                try:
                    data = response.json()
                    print(json.dumps(data, indent=2))
                    content = ""
                    if "choices" in data:
                        content = data['choices'][0]['message']['content']
                    elif "message" in data: # Ollama format sometimes
                        content = data['message']['content']
                        
                    print(f"\nExtracted Content: {content}")
                    print("✅ LLM Connection Successful!")
                    success = True
                    break
                except Exception as e:
                    print(f"Failed to parse JSON: {e}")
                    print(response.text)
            else:
                print(f"Error Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("Connection Refused (Is the server running?)")
        except Exception as e:
            print(f"Error: {e}")
            
    if not success:
        print("\n\nALL CONNECTION ATTEMPTS FAILED")
        print("Please ensure your local LLM server (vLLM or Ollama) is running.")
        print("Expected model:", model)

if __name__ == "__main__":
    # Force UTF-8 for Windows console
    import sys
    if sys.platform.startswith("win"):
        sys.stdout.reconfigure(encoding='utf-8')
    test_llm_connection()
