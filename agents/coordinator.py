from models.schemas import AgentRole, Domain, TaskDecomposition
from services.qwen_client import chat_json
from config import QWEN_MODEL

SYSTEM_PROMPT = """You are the Coordinator of the STEM Mentor Society — a multi-agent AI tutoring system.
Your job is to analyze student questions, identify which scientific domains are relevant, and decompose the question into targeted sub-questions for each specialist agent.

The available specialist agents are:
- math: Prof. Ada — algebra, calculus, statistics, proofs, discrete math
- physics: Dr. Newton — mechanics, electromagnetism, quantum, thermodynamics
- cs: Eng. Turing — algorithms, data structures, ML, programming, complexity
- chembio: Dr. Curie — chemistry, biochemistry, molecular biology, genetics

Guidelines:
- Only assign domains that are genuinely relevant (1-4 domains)
- For each domain, craft a specific sub-question that targets that agent's expertise
- Assess complexity: simple (1 domain, direct answer), moderate (2 domains, some integration), complex (3+ domains, interdisciplinary)
- Always include at least 1 domain"""


class CoordinatorAgent:
    role = AgentRole.COORDINATOR
    name = "Director (Coordinator)"
    emoji = "🎓"
    model = QWEN_MODEL

    async def decompose(self, question: str, student_level: str) -> TaskDecomposition:
        prompt = f"""Student level: {student_level}
Student question: "{question}"

Analyze this question and respond in JSON:
{{
  "domains": ["math", "physics", "cs", "chembio"],  // only include relevant ones
  "sub_questions": {{
    "math": "specific math sub-question (if relevant)",
    "physics": "specific physics sub-question (if relevant)",
    "cs": "specific cs sub-question (if relevant)",
    "chembio": "specific chembio sub-question (if relevant)"
  }},
  "reasoning": "why you chose these domains",
  "complexity": "simple|moderate|complex"
}}

Only include domains that are genuinely relevant. The sub_questions object should only have keys for selected domains."""

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        data = await chat_json(messages, model=self.model)

        raw_domains = data.get("domains", ["general"])
        valid_domains = []
        for d in raw_domains:
            try:
                valid_domains.append(Domain(d))
            except ValueError:
                pass
        if not valid_domains:
            valid_domains = [Domain.GENERAL]

        raw_sub = data.get("sub_questions", {})
        sub_questions = {}
        for domain in valid_domains:
            if domain.value in raw_sub:
                sub_questions[domain] = raw_sub[domain.value]
            else:
                sub_questions[domain] = question

        return TaskDecomposition(
            domains=valid_domains,
            sub_questions=sub_questions,
            reasoning=data.get("reasoning", ""),
            complexity=data.get("complexity", "moderate"),
        )
