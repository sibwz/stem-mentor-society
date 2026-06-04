import asyncio
from typing import AsyncGenerator
import json

from models.schemas import (
    AgentRole, Domain, AgentMessage, MessageType,
    DomainResponse, DebateRound, FinalAnswer, TaskDecomposition,
)
from agents.coordinator import CoordinatorAgent
from agents.math_agent import MathAgent
from agents.physics_agent import PhysicsAgent
from agents.cs_agent import CSAgent
from agents.chembio_agent import ChemBioAgent
from agents.synthesizer import SynthesizerAgent
from agents.base_agent import BaseAgent
from config import MAX_DEBATE_ROUNDS


DOMAIN_AGENTS: dict[Domain, BaseAgent] = {
    Domain.MATH: MathAgent(),
    Domain.PHYSICS: PhysicsAgent(),
    Domain.CS: CSAgent(),
    Domain.CHEMBIO: ChemBioAgent(),
}

coordinator = CoordinatorAgent()
synthesizer = SynthesizerAgent()


def _msg(agent: AgentRole, type: MessageType, content: str, round: int = 0) -> str:
    return json.dumps(AgentMessage(agent=agent, type=type, content=content, round=round).model_dump())


async def run_session(
    question: str, student_level: str
) -> AsyncGenerator[str, None]:
    # 1. Coordinator decomposes the task
    yield _msg(
        AgentRole.COORDINATOR, MessageType.THINKING,
        f"Analyzing your question and identifying which STEM domains are relevant..."
    )

    try:
        decomposition: TaskDecomposition = await coordinator.decompose(question, student_level)
    except Exception as e:
        yield _msg(AgentRole.COORDINATOR, MessageType.ERROR, f"Decomposition failed: {e}")
        return

    domain_list = ", ".join(d.value for d in decomposition.domains)
    yield _msg(
        AgentRole.COORDINATOR, MessageType.SPEAKING,
        f"**Task Decomposition Complete**\n\n"
        f"Domains involved: {domain_list}\n"
        f"Complexity: {decomposition.complexity}\n\n"
        f"**Reasoning:** {decomposition.reasoning}"
    )

    # 2. Domain agents analyze in parallel
    active_agents = [
        DOMAIN_AGENTS[d] for d in decomposition.domains
        if d in DOMAIN_AGENTS
    ]

    if not active_agents:
        yield _msg(AgentRole.COORDINATOR, MessageType.ERROR, "No valid domain agents found.")
        return

    for agent in active_agents:
        yield _msg(
            agent.role, MessageType.THINKING,
            f"Analyzing from {agent.name}'s perspective..."
        )

    async def fetch_response(agent: BaseAgent) -> DomainResponse:
        sub_q = decomposition.sub_questions.get(agent.domain, question)
        return await agent.analyze(question, sub_q, student_level)

    tasks = [fetch_response(a) for a in active_agents]
    responses: list[DomainResponse] = await asyncio.gather(*tasks)

    for resp in responses:
        agent_obj = DOMAIN_AGENTS.get(resp.domain)
        emoji = agent_obj.emoji if agent_obj else ""
        yield _msg(
            resp.agent, MessageType.SPEAKING,
            f"{emoji} **{resp.agent.value.upper()} Analysis** [Confidence: {resp.confidence:.0%}]\n\n"
            f"{resp.answer}\n\n"
            f"**Key Points:**\n" + "\n".join(f"• {p}" for p in resp.key_points)
        )

    # 3. Synthesizer checks for conflicts → debate if needed
    yield _msg(
        AgentRole.SYNTHESIZER, MessageType.THINKING,
        "Reviewing all agent responses for conflicts or complementary insights..."
    )

    debate_rounds: list[DebateRound] = []

    if len(responses) >= 2:
        conflicts = await synthesizer.find_conflicts(responses)

        if conflicts:
            yield _msg(
                AgentRole.SYNTHESIZER, MessageType.STATUS,
                f"**Conflicts Detected!** Found {len(conflicts)} point(s) of disagreement. Starting debate..."
            )

            for round_num in range(1, MAX_DEBATE_ROUNDS + 1):
                topic = conflicts[0] if conflicts else "approach to the problem"
                yield _msg(
                    AgentRole.SYNTHESIZER, MessageType.STATUS,
                    f"**Debate Round {round_num}:** {topic}",
                    round=round_num,
                )

                other_views: dict[AgentRole, str] = {
                    r.agent: r.answer[:200] for r in responses
                }

                debate_args: dict[AgentRole, str] = {}
                debate_tasks = []
                for agent in active_agents:
                    peers = {k: v for k, v in other_views.items() if k != agent.role}
                    debate_tasks.append(
                        agent.debate_argument(topic, {k.value: v for k, v in peers.items()}, round_num, student_level)
                    )

                raw_args = await asyncio.gather(*debate_tasks)
                for agent, arg in zip(active_agents, raw_args):
                    debate_args[agent.role] = arg
                    yield _msg(
                        agent.role, MessageType.DEBATE,
                        f"**Round {round_num}:** {arg}",
                        round=round_num,
                    )

                consensus = None
                if round_num == MAX_DEBATE_ROUNDS:
                    consensus = "Agents have shared their perspectives; synthesis will integrate all views."

                debate_rounds.append(DebateRound(
                    round_number=round_num,
                    topic=topic,
                    arguments=debate_args,
                    consensus=consensus,
                ))

                if len(conflicts) <= 1:
                    break
                conflicts = conflicts[1:]

    # 4. Final synthesis
    yield _msg(
        AgentRole.SYNTHESIZER, MessageType.THINKING,
        "Weaving all perspectives into a unified answer for you..."
    )

    synthesis = await synthesizer.synthesize(question, responses, debate_rounds, student_level)

    yield _msg(AgentRole.SYNTHESIZER, MessageType.SYNTHESIS, synthesis)

    final = FinalAnswer(
        question=question,
        domain_responses=responses,
        debate_rounds=debate_rounds,
        synthesis=synthesis,
        total_agents_involved=len(active_agents) + 2,  # +coordinator +synthesizer
    )
    yield _msg(
        AgentRole.COORDINATOR, MessageType.STATUS,
        json.dumps({"summary": f"{final.total_agents_involved} agents collaborated", "done": True})
    )
