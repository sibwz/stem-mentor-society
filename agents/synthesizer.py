from models.schemas import AgentRole, DomainResponse, DebateRound
from services.qwen_client import chat, chat_json
from config import QWEN_MODEL

SYSTEM_PROMPT = """You are the Synthesizer of the STEM Mentor Society — the final integrator of multi-agent knowledge.
Your role:
1. Identify conflicts or complementary insights across agent responses
2. Weave multiple perspectives into a single coherent, comprehensive answer
3. Ensure the explanation is appropriate for the student's level
4. Highlight the interdisciplinary nature of the answer when applicable

You are not a domain expert — you are a master educator who knows how to unite diverse expertise into understanding."""


class SynthesizerAgent:
    role = AgentRole.SYNTHESIZER
    name = "Mentor Synthesis"
    emoji = "✨"
    model = QWEN_MODEL

    async def find_conflicts(
        self, responses: list[DomainResponse]
    ) -> list[str]:
        if len(responses) < 2:
            return []

        summaries = "\n".join(
            f"- {r.agent.value}: {r.answer[:300]}..." for r in responses
        )
        prompt = f"""Multiple specialist agents have answered a student question. Review their responses and identify any contradictions, disagreements, or points where they make different assumptions:

{summaries}

Respond in JSON:
{{
  "conflicts": ["description of conflict 1", "description of conflict 2"],  // empty list if none
  "has_conflicts": true|false
}}"""

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        data = await chat_json(messages, model=self.model)
        if data.get("has_conflicts"):
            return data.get("conflicts", [])
        return []

    async def synthesize(
        self,
        question: str,
        responses: list[DomainResponse],
        debate_rounds: list[DebateRound],
        student_level: str,
    ) -> str:
        agents_summary = "\n\n".join(
            f"**{r.agent.value.upper()} ({r.domain.value})** [confidence: {r.confidence:.0%}]:\n{r.answer}\nKey points: {', '.join(r.key_points)}"
            for r in responses
        )

        debate_summary = ""
        if debate_rounds:
            debate_summary = "\n\nDebate outcomes:\n" + "\n".join(
                f"Round {d.round_number} on '{d.topic}': {d.consensus or 'ongoing'}"
                for d in debate_rounds
            )

        prompt = f"""Student level: {student_level}
Student question: "{question}"

Agent responses:
{agents_summary}{debate_summary}

Synthesize all perspectives into one clear, comprehensive answer for the student.
- Start with the big picture, then go into detail
- Acknowledge where different disciplines each contributed
- If there were debates, explain the resolution
- Use markdown formatting (headers, bold, bullet points) for clarity
- End with 2-3 follow-up questions to deepen understanding"""

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        return await chat(messages, model=self.model, temperature=0.6)
