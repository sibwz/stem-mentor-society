from pydantic import BaseModel
from enum import Enum
from typing import Optional


class Domain(str, Enum):
    MATH = "math"
    PHYSICS = "physics"
    CS = "cs"
    CHEMBIO = "chembio"
    GENERAL = "general"


class AgentRole(str, Enum):
    COORDINATOR = "coordinator"
    MATH = "math"
    PHYSICS = "physics"
    CS = "cs"
    CHEMBIO = "chembio"
    SYNTHESIZER = "synthesizer"


class MessageType(str, Enum):
    THINKING = "thinking"
    SPEAKING = "speaking"
    DEBATE = "debate"
    SYNTHESIS = "final"
    ERROR = "error"
    STATUS = "status"


class AgentMessage(BaseModel):
    agent: AgentRole
    type: MessageType
    content: str
    round: int = 0


class TaskDecomposition(BaseModel):
    domains: list[Domain]
    sub_questions: dict[Domain, str]
    reasoning: str
    complexity: str  # "simple" | "moderate" | "complex"


class DomainResponse(BaseModel):
    domain: Domain
    agent: AgentRole
    answer: str
    confidence: float  # 0.0 - 1.0
    key_points: list[str]


class DebateRound(BaseModel):
    round_number: int
    topic: str
    arguments: dict[AgentRole, str]
    consensus: Optional[str] = None


class SessionRequest(BaseModel):
    question: str
    student_level: str = "high_school"  # "middle_school" | "high_school" | "undergraduate" | "graduate"


class FinalAnswer(BaseModel):
    question: str
    domain_responses: list[DomainResponse]
    debate_rounds: list[DebateRound]
    synthesis: str
    total_agents_involved: int
