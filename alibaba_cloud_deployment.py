"""
Proof of Alibaba Cloud deployment.

This file demonstrates direct use of Alibaba Cloud DashScope (Qwen Cloud)
API to run STEM Mentor Society agents on Alibaba Cloud infrastructure.

Run with:  python alibaba_cloud_deployment.py
"""

import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# Alibaba Cloud DashScope endpoint — this IS the Alibaba Cloud service
ALIBABA_CLOUD_ENDPOINT = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_MODEL = "qwen-max"


async def verify_alibaba_cloud_connection():
    """Verify connectivity to Alibaba Cloud DashScope and run a sample agent turn."""
    api_key = os.getenv("QWEN_API_KEY", "")
    if not api_key:
        print("ERROR: QWEN_API_KEY not set in environment.")
        return

    client = AsyncOpenAI(
        api_key=api_key,
        base_url=ALIBABA_CLOUD_ENDPOINT,
    )

    print(f"Connecting to Alibaba Cloud DashScope...")
    print(f"Endpoint: {ALIBABA_CLOUD_ENDPOINT}")
    print(f"Model: {QWEN_MODEL}")
    print("-" * 60)

    # Simulate the Math Agent answering a question
    response = await client.chat.completions.create(
        model=QWEN_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are Prof. Ada, a math professor at STEM Mentor Society, a multi-agent AI tutoring system deployed on Alibaba Cloud."
            },
            {
                "role": "user",
                "content": "Briefly explain what a derivative is for a high school student."
            }
        ],
        max_tokens=256,
    )

    answer = response.choices[0].message.content
    model_used = response.model
    usage = response.usage

    print(f"[ALIBABA CLOUD RESPONSE RECEIVED]")
    print(f"Model: {model_used}")
    print(f"Tokens used: {usage.total_tokens} (prompt: {usage.prompt_tokens}, completion: {usage.completion_tokens})")
    print(f"\nAgent Response:\n{answer}")
    print("-" * 60)
    print("Alibaba Cloud DashScope connection verified successfully.")


if __name__ == "__main__":
    asyncio.run(verify_alibaba_cloud_connection())
