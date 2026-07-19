import os
from pathlib import Path

import openai

api_key_path = Path(__file__).resolve().parents[1] / ".secrets" / "openai_api_key"
api_key = api_key_path.read_text(encoding="utf-8").strip()
if not api_key:
    raise RuntimeError(f"API key file is empty: {api_key_path}")

base_url_path = Path(__file__).resolve().parents[1] / ".secrets" / "openai_base_url"
base_url = os.getenv("OPENAI_BASE_URL")
if not base_url and base_url_path.is_file():
    base_url = base_url_path.read_text(encoding="utf-8").strip()

client_kwargs = {"api_key": api_key}
if base_url:
    client_kwargs["base_url"] = base_url
client = openai.OpenAI(**client_kwargs)

response = client.chat.completions.create(
    model="auto-std",
    messages=[
        {
            "role": "user",
            "content": "你好，你是什么模型"
        }
    ]
)

print(response)
