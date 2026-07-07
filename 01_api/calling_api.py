import os

import openai

api_key = os.environ["OPENAI_API_KEY"]
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
    ]
)

print(response)
