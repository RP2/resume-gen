# utils/llm.py
"""
AI provider interaction utilities (OpenAI, Anthropic, etc.)
"""

import requests

def call_openai(prompt: str, api_key: str, model: str, max_tokens: int = 1500) -> str:
    """Call OpenAI API with error handling and optimized parameters.
    
    Args:
        prompt: The input prompt
        api_key: OpenAI API key
        model: Model name (e.g. 'gpt-4')
        max_tokens: Maximum tokens in response (default 1500 for resume generation)
    
    Returns:
        Generated text response
        
    Raises:
        requests.exceptions.RequestException: For API connection errors
        ValueError: For invalid responses or missing data
    """
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a professional resume writer."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7,  # Keep moderate creativity
        "presence_penalty": 0.1,  # Slight penalty to avoid repetition
        "frequency_penalty": 0.1  # Slight penalty to improve diversity
    }
    
    try:
        resp = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=120  # 2 minute timeout for longer generations
        )
        resp.raise_for_status()
        response_json = resp.json()
        
        # Validate response structure
        if not response_json.get("choices"):
            raise ValueError("No choices in OpenAI response")
            
        choice = response_json["choices"][0]
        if not choice.get("message"):
            raise ValueError("No message in OpenAI response choice")
            
        content = choice["message"].get("content")
        if not content:
            raise ValueError("No content in OpenAI response message")
            
        return content
            
    except requests.exceptions.Timeout:
        raise RuntimeError("OpenAI API request timed out")
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                error_message = error_detail.get('error', {}).get('message', str(e))
                raise RuntimeError(f"OpenAI API request failed: {error_message}")
            except (ValueError, AttributeError):
                # If we can't parse the error JSON, fall back to the basic error
                raise RuntimeError(f"OpenAI API request failed: {str(e)}")
        else:
            raise RuntimeError(f"OpenAI API request failed: {str(e)}")
    except (KeyError, ValueError) as e:
        raise ValueError(f"Invalid OpenAI API response: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error calling OpenAI API: {str(e)}")

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
