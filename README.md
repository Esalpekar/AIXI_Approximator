# LLM-AIXI

AIXI (Hutter 2005) is a formalization of a universal, ideal, and uncomputable agent that maximizes a reward metric in an unknown environment. This project explores how many practical deviations from this ideal must be taken to achieve a functional agent.

See [Instructions/Background.txt](Instructions/Background.txt) for complete theoretical background.

## Theory

This is a purely qualitative instantiation of a Bayesian AIXI reasoner. The operational philosophy is that quantitative data is just compressed qualitative data. Data in the form of an essay contains all the necessary information; it is just not compressed.

### Core Components

- **Constitution**: Serves as the agent's moral and productive guide
- **Judge**: Evaluates each action against the constitution and returns a detailed report (reward percept)
- **Subenvironments**: Tools recast as self-manifested models of the true environment
- **Ideator**: Proposes actions based on full history, constitution, and tool templates
- **History**: Complete, uncompressed record of all action-perception cycles

### Operating Loop

1. Agent selects a subenvironment and generates input text
2. Environment returns tool result and judge's constitutional evaluation
3. Both are added to agent's complete history for next cycle
4. Process repeats for fixed number of cycles (finite lifespan)

### Deviations from True AIXI

- LLM reasoning replaces uncomputable Solomonoff induction
- Environment split into true environment (judge) and modeled subenvironments
- Starts with prior knowledge (LLM training, constitution)
- Finite cycles rather than infinite horizon
- Qualitative rather than quantitative optimization

## Features

- Constitutional governance with ethical safeguards
- Judge-based evaluation and learning
- Four subenvironments: file system, web search, code execution, LLM consultation
- Complete history maintenance without compression
- Token usage tracking and cost estimation
- Secure, restricted tool access
- Detailed execution logging

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Configure Google Cloud Vertex AI credentials
3. Copy `Config/.env.example` to `Config/.env` and set your project ID
4. Set objective in `data/constitution.txt`
5. Run: `python main.py`

## Project Structure

```
agent/              # Core reasoning (Ideator, data models)
environment/        # Judge and orchestrator
subenvironments/    # Tool implementations
utils/              # Token tracking
Config/             # API configuration
data/               # Constitution
Histories/          # Execution logs
Working Directory/  # Agent workspace
```

## Educational Purpose

This project is a lesson in agent design, intended for educational purposes where optimization and scalability are not primary concerns. It demonstrates practical approximation of theoretical optimal agents using modern language models.
