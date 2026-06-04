# 🎓 STEM Mentor Society

> **Global AI Hackathon — Track 3: Agent Society**
> A production-grade multi-agent AI tutoring system powered by Qwen Cloud.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Qwen Cloud](https://img.shields.io/badge/Powered%20by-Qwen%20Cloud-purple.svg)](https://dashscope.aliyuncs.com)

## What It Does

STEM Mentor Society is a multi-agent AI tutoring platform where **six specialized AI agents** collaborate, debate, and synthesize answers to any STEM question. Each agent has a distinct personality, expertise, and role — and they **talk to each other** in real time, visible to the student.

### The Agents

| Agent | Role | Personality |
|-------|------|-------------|
| 🎓 **Coordinator** | Decomposes tasks, assigns roles | Analytical, strategic |
| 🔢 **Prof. Ada (Math)** | Mathematical analysis & proofs | Precise, rigorous |
| ⚛️ **Dr. Newton (Physics)** | Physical intuition & models | Intuitive, analogical |
| 💻 **Eng. Turing (CS)** | Algorithms & implementation | Systematic, efficient |
| 🧬 **Dr. Curie (Chem/Bio)** | Molecular & biological insight | Curious, experimental |
| ✨ **Synthesizer** | Detects conflicts, unifies answers | Integrative, educational |

## Architecture

```
                         Student Question
                               │
                    ┌──────────▼──────────┐
                    │   🎓 Coordinator    │
                    │  Task Decomposition │
                    │  Domain Routing     │
                    └──────────┬──────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
   ┌──────▼──────┐    ┌────────▼───────┐   ┌───────▼──────┐
   │ 🔢 Math    │    │ ⚛️ Physics     │   │ 💻 CS        │
   │ Prof. Ada  │    │ Dr. Newton     │   │ Eng. Turing  │
   └──────┬──────┘    └────────┬───────┘   └───────┬──────┘
          │                    │                    │
          │            ┌───────▼──────┐             │
          │            │ 🧬 Chem/Bio  │             │
          │            │ Dr. Curie    │             │
          │            └───────┬──────┘             │
          └────────────────────┼────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   ✨ Synthesizer    │
                    │  Conflict Detection │
                    │  Agent Debate       │
                    │  Final Synthesis    │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Unified Answer    │
                    │   + Follow-up Qs    │
                    └─────────────────────┘
```

### Infrastructure (Alibaba Cloud)

```
  Browser ──WebSocket──► FastAPI Server (ECS)
                              │
                    ┌─────────▼─────────┐
                    │  Qwen Cloud API   │
                    │  (DashScope)      │
                    │  qwen-max model   │
                    └───────────────────┘
```

## Key Features

- **Task Decomposition**: Coordinator identifies which domains a question touches and crafts targeted sub-questions for each specialist
- **Parallel Agent Processing**: Domain agents analyze simultaneously for speed
- **Conflict Detection**: Synthesizer automatically identifies when agents disagree or make contradictory assumptions
- **Agent Debate**: When conflicts are found, agents argue their positions across multiple rounds
- **Real-time Streaming**: WebSocket streams each agent's thinking, speaking, and debating live to the student
- **Level-adaptive**: Responses adapt from middle school to graduate level
- **Interdisciplinary synthesis**: Final answer weaves all perspectives together

## Setup

### 1. Get a Qwen Cloud API Key
Sign up at [Alibaba Cloud DashScope](https://dashscope.aliyuncs.com) and create an API key.

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env and add your QWEN_API_KEY
```

### 4. Run
```bash
python main.py
```

Open http://localhost:8000 in your browser.

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve frontend |
| `/api/health` | GET | Health check |
| `/api/ask` | POST | REST endpoint (full session) |
| `/api/ws/session` | WebSocket | Real-time streaming session |

### WebSocket Protocol
```json
// Send
{ "question": "...", "student_level": "high_school" }

// Receive (streamed)
{ "agent": "math", "type": "speaking", "content": "...", "round": 0 }

// Done
{ "done": true }
```

## Example Questions to Try

- *"How do sorting algorithms work, and what's the best one?"* → CS + Math
- *"Why does E=mc²?"* → Physics + Math
- *"How does DNA store and replicate information?"* → Chem/Bio + CS + Math
- *"Explain neural networks from first principles"* → CS + Math + Physics

## Alibaba Cloud Deployment

See [`alibaba_cloud_deployment.py`](alibaba_cloud_deployment.py) for proof of Alibaba Cloud integration via the DashScope SDK.

The backend is deployed on **Alibaba Cloud ECS** using the Qwen Cloud API at:
`https://dashscope.aliyuncs.com/compatible-mode/v1`

## Track

**Track 3: Agent Society** — Multi-agent collaboration with task division, dialogue, negotiation, and synthesis.

## License

MIT — see [LICENSE](LICENSE)
