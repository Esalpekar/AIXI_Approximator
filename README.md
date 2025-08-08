# LLM AIXI

A practical implementation of AIXI using Large Language Models. This project was meant to explore the creation of agentic structures from scratch. To stay fundamental, itexplores how many deviations from Hutter's ideal universal agent are necessary to create a functional system.

## Overview

AIXI (Hutter 2005) formalizes a universal, ideal, and uncomputable agent that maximizes reward in unknown environments. This implementation adapts AIXI to work with LLMs through several key modifications:

- **Constitution-based guidance**: A text-based moral and productive framework guides agent behavior
- **Judge-based evaluation**: Each action is evaluated against the constitution, providing detailed feedback as the reward signal
- **Sub-environments as tools**: Tools are recast as self-manifested models of the environment that can be sampled for observations
- **Text-only data flow**: All information remains in high-fidelity text format, leveraging attention mechanisms for compression rather than quantitative metrics

## Architecture

The system consists of:

- **Agent**: LLM-powered decision maker that selects actions based on constitution and history
- **Judge**: Evaluates actions against the constitution and provides detailed reward essays
- **Orchestrator**: Routes actions to appropriate sub-environments and coordinates evaluation
- **Sub-environments**: Tools including code execution, web search, file system, and human consultation


## Reference

Based on Marcus Hutter's AIXI framework: https://arxiv.org/abs/cs/0004001
