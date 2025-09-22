import requests
import json
from openai import OpenAI
from typing import Any, Tuple, Optional

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)


def general_call(text: Optional[str] = None,
                 temperature: float = 0.0, 
                 llm_model: str = "gpt-4.1-nano", 
                 messages: Optional[list] = None) -> Tuple[str, Any]:

    if "gpt" in llm_model:
        return link_ai_call(text, temperature=temperature, llm_model=llm_model, messages=messages)
    elif "qwen" in llm_model:
        return qwen_call(text, temperature=temperature, llm_model=llm_model, messages=messages)
    elif "deepseek" in llm_model:
        return deepseek_call(text, temperature=temperature, llm_model=llm_model, messages=messages)
    else:
        raise ValueError(f"Unsupported: {llm_model}\nYou need to configure the model and provider yourself")


def link_ai_call(text: Optional[str] = None,
                 temperature: float = 0.0, 
                 llm_model: str = "gpt-4.1-nano", 
                 messages: Optional[list] = None) -> Tuple[str, Any]:
    
    # Get configuration from config.json
    link_ai_config = config["api_providers"]["link_ai"]
    base_url = link_ai_config["base_url"]
    api_key = link_ai_config["api_key"]
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    body = {
        "app_code": "",
        "model": llm_model,
        "messages": [{
            "role": "user",
            "content": text
        }] if messages is None else messages,
        "temperature": temperature
    }
    res = requests.post(base_url, json=body, headers=headers)
    if res.status_code == 200:
        reply_text = res.json().get("choices")[0]['message']['content']
        results = reply_text
        token_usage = res.json().get("usage")
        from types import SimpleNamespace
        token_usage = SimpleNamespace(**token_usage)
    else:
        error = res.json()
        results = f"Request exception, error code={error.get('code')}, error message={error.get('message')}"
        raise Exception(results)
    return results, token_usage


def qwen_call(text: Optional[str] = None, 
              temperature: float = 0.0, 
              llm_model: str = "qwen3-32b",
              messages: Optional[list] = None) -> Tuple[str, Any]:
    
    # Get configuration from config.json
    qwen_config = config["api_providers"]["qwen"]
    base_url = qwen_config["base_url"]
    api_key = qwen_config["api_key"]
    
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )
    completion = client.chat.completions.create(
        model=llm_model,
        messages=[
            {
                "role": "user",
                "content": text
            },
        ] if messages is None else messages,  # type: ignore
        temperature=temperature,
        stream=True,
        stream_options={"include_usage": True},
        extra_body={"enable_thinking": False},
    )

    full_content = ""
    usage = None
    for chunk in completion:
        if chunk.choices and chunk.choices[0].delta.content is not None:
            full_content += chunk.choices[0].delta.content
        if chunk.usage is not None:
            usage = chunk.usage
    return full_content, usage



def deepseek_call(text: Optional[str] = None,
                  temperature: float = 0.0,
                  llm_model: str = "deepseek-chat",
                  messages: Optional[list] = None) -> Tuple[str, Any]:
    
    # Get configuration from config.json
    deepseek_config = config["api_providers"]["deepseek"]
    base_url = deepseek_config["base_url"]
    api_key = deepseek_config["api_key"]
    
    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
    )
    completion = client.chat.completions.create(
        model=llm_model,
        messages=[
            {
                "role": "user",
                "content": text
            },
        ] if messages is None else messages, # type: ignore
        temperature=temperature)

    full_content = completion.choices[0].message.content or ""
    return full_content, completion.usage
