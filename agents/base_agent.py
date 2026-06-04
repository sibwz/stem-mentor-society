from abc import ABC, abstractmethod
from models.schemas import AgentRole, DomainResponse, Domain
from services.qwen_client import chat, chat_json
from config import QWEN_MODEL


class BaseAgent(ABC):
    role: AgentRole
    domain: Domain
    name: str
    emoji: str
    personality: str
    expertise: str

    def __init__(self):
        self.model = QWEN_MODEL

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        pass

    def _build_messages(self, user_content: str, extra_context: str = "") -> list[dict]:
        system = self.system_prompt
        if extra_context:
            system += f"\n\nAdditional context from other agents:\n{extra_context}"
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user_content},
        ]

    async def analyze(
        self,
        question: str,
        sub_question: str,
        student_level: str,
        extra_context: str = "",
    ) -> DomainResponse:
        prompt = f"""Student level: {student_level}

Original question: {question}

Your specific sub-question to address: {sub_question}

Respond in JSON with these fields:
{{
  "answer": "your detailed explanation",
  "confidence": 0.0-1.0,
  "key_points": ["point1", "point2", "point3"]
}}"""
        messages = self._build_messages(prompt, extra_context)
        data = await chat_json(messages, model=self.model)

        return DomainResponse(
            domain=self.domain,
            agent=self.role,
            answer=data.get("answer", ""),
            confidence=float(data.get("confidence", 0.8)),
            key_points=data.get("key_points", []),
        )

    async def debate_argument(
        self,
        topic: str,
        other_views: dict[str, str],
        round_num: int,
        student_level: str,
    ) -> str:
        others_text = "\n".join(
            f"- {agent}: {view}" for agent, view in other_views.items()
        )
        prompt = f"""Debate round {round_num}.

Topic of disagreement: {topic}

Other agents' positions:
{others_text}

As {self.name}, state your position clearly. You may agree, partially agree, or respectfully disagree with specific reasoning. Be concise (2-3 sentences)."""

        messages = self._build_messages(prompt)
        return await chat(messages, model=self.model, temperature=0.8)
