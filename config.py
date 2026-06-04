import os
from dotenv import load_dotenv

load_dotenv()

QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-max")
QWEN_FAST_MODEL = os.getenv("QWEN_FAST_MODEL", "qwen-turbo")

MAX_DEBATE_ROUNDS = int(os.getenv("MAX_DEBATE_ROUNDS", "2"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))
