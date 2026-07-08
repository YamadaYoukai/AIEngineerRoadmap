# Structured Output

Run:

```bash
python3 03_structured_output/structured_output.py "RAG evaluation"
```

The script reads the API key from `../.secrets/openai_api_key`, calls the same
LLM proxy used by the other examples, and requests a strict JSON Schema response.
The printed result is parsed JSON, not raw model text.
