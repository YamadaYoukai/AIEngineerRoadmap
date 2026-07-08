import json
import sys
from pathlib import Path
from typing import Any
from model import IncidentAnalysis

import openai

API_KEY_PATH = Path(__file__).resolve().parents[1] / ".secrets" / "openai_api_key"
LLM_PROXY = "https://llm-proxy.intra.xiaojukeji.com"
MODEL = "auto-std"

LEARNING_PLAN_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "topic": {
            "type": "string",
            "description": "The learning topic requested by the user.",
        },
        "level": {
            "type": "string",
            "enum": ["beginner", "intermediate", "advanced"],
        },
        "summary": {
            "type": "string",
            "description": "A concise summary of the recommended learning path.",
        },
        "prerequisites": {
            "type": "array",
            "items": {"type": "string"},
        },
        "milestones": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "objective": {"type": "string"},
                    "tasks": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "estimated_hours": {
                        "type": "integer",
                        "minimum": 1,
                    },
                },
                "required": [
                    "name",
                    "objective",
                    "tasks",
                    "estimated_hours",
                ],
                "additionalProperties": False,
            },
        },
        "next_action": {
            "type": "string",
            "description": "The first concrete action the learner should take.",
        },
    },
    "required": [
        "topic",
        "level",
        "summary",
        "prerequisites",
        "milestones",
        "next_action",
    ],
    "additionalProperties": False,
}


def read_api_key() -> str:
    api_key = API_KEY_PATH.read_text(encoding="utf-8").strip()
    if not api_key:
        raise RuntimeError(f"API key file is empty: {API_KEY_PATH}")
    return api_key


def build_client() -> openai.OpenAI:
    return openai.OpenAI(
        api_key=read_api_key(),
        base_url=LLM_PROXY,
    )


def create_learning_plan(topic: str) -> dict[str, Any]:
    client = build_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI engineering mentor. Produce practical, "
                    "implementation-oriented learning plans."
                ),
            },
            {
                "role": "user",
                "content": f"Create a concise learning plan for: {topic}",
            },
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "learning_plan",
                "schema": LEARNING_PLAN_SCHEMA,
                "strict": True,
            },
        },
    )

    message = response.choices[0].message
    refusal = getattr(message, "refusal", None)
    if refusal:
        raise RuntimeError(f"Model refused the request: {refusal}")

    if not message.content:
        raise RuntimeError("Model returned an empty structured output.")

    return json.loads(message.content)


def analysis_incident(problem: str) -> IncidentAnalysis:
    client = build_client()
    print("发现问题中..." + problem)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一个专业的 Java 软件工程师，擅长排查线上问题。"
                    "请根据用户提供的问题，输出结构化的故障分析结果。"
                    "不要编造不存在的事实；如果信息不足，请在 next_steps 中说明需要补充哪些信息。"
                ),
            },
            {
                "role": "user",
                "content": f"我遇到了这个问题，急需解决：{problem}",
            },
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "incident_analysis",
                "schema": IncidentAnalysis.model_json_schema(),
                "strict": True,
            },
        },
    )

    message = response.choices[0].message
    refusal = getattr(message, "refusal", None)
    if refusal:
        raise RuntimeError(f"Model refused the request: {refusal}")

    if not message.content:
        raise RuntimeError("Model returned an empty structured output.")

    return IncidentAnalysis.model_validate_json(message.content)


def main() -> None:
    problem = " ".join(sys.argv[1:]).strip()
    if not problem:
        problem = input("请输入故障描述：").strip()

    if not problem:
        raise RuntimeError("故障描述不能为空。")

    result = analysis_incident(problem)
    print("\n分析结果：")
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
