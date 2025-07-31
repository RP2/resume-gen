# utils/llm.py
"""
AI provider interaction utilities (OpenAI, Anthropic, etc.)
"""

import requests

def call_openai(prompt: str, api_key: str, model: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a professional resume writer."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 2048,
        "temperature": 0.7
    }
    resp = requests.post(url, headers=headers, json=data, timeout=60)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

# Placeholder for Anthropic Claude
# def call_claude(prompt: str, api_key: str, model: str) -> str:
#     ...

# Add more providers as needed

def call_ai_provider(prompt: str, provider: str, api_key: str, model: str) -> str:
    if provider == "openai":
        return call_openai(prompt, api_key, model)
    # elif provider == "anthropic":
    #     return call_claude(prompt, api_key, model)
    else:
        raise ValueError(f"Unknown AI provider: {provider}")
