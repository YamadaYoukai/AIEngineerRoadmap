from pathlib import Path

import openai

api_key_path = Path(__file__).resolve().parents[1] / ".secrets" / "openai_api_key"
api_key = api_key_path.read_text(encoding="utf-8").strip()
if not api_key:
    raise RuntimeError(f"API key file is empty: {api_key_path}")

llm_proxy = "https://llm-proxy.intra.xiaojukeji.com"

client = openai.OpenAI(
    api_key=api_key,
    base_url=llm_proxy
)

response = client.chat.completions.create(
    model="auto-std",
    messages=[
        {
            "role": "user",
            "content": "你好，你是什么模型"
        }
    ],
    stream=True
)

for chunk in response:
    for choice in chunk.choices:
        if choice.delta is not None and choice.delta.content is not None:
            print(choice.delta.content, end="")
