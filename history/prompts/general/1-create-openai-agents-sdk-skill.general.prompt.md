---
id: 1
title: Create OpenAI Agents SDK Skill
stage: general
date: 2026-01-27
surface: agent
model: Claude Opus 4.5
feature: none
branch: 001-phishing-email-scanner
user: user
command: create openai-agents-sdk skill
labels: [skill, openai, agents, gemini, integration]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .claude/skills/openai-agents-sdk/SKILL.md
 - .claude/skills/openai-agents-sdk/scripts/gemini_agent_example.py
 - .claude/skills/openai-agents-sdk/references/providers_guide.md
 - .claude/skills/openai-agents-sdk/assets/configuration_template.md
tests:
 - none
---

## Prompt

Create a skill name openai-agents-sdk and use skill-creator-pro for making this skill and analyze the given links that how we use openai agents sdk with gemini client.

https://github.com/panaversity/learn-agentic-ai/blob/main/01_ai_agents_first/04_hello_agent/hello_agent/main.py

https://github.com/panaversity/learn-agentic-ai/tree/main/01_ai_agents_first

## Response snapshot

Created a comprehensive openai-agents-sdk skill that demonstrates how to use the OpenAI Agents SDK with different LLM providers, particularly Google Gemini. The skill includes:

- Main SKILL.md file with configuration examples for both OpenAI and Gemini
- Python script demonstrating practical usage with both providers
- Reference documentation with advanced patterns and best practices
- Configuration template asset for easy setup

The implementation shows how to configure the OpenAI client to work with Google's Gemini API through the OpenAI-compatible endpoint at "https://generativelanguage.googleapis.com/v1beta/openai/", allowing the use of Gemini models like "gemini-2.5-flash" with the familiar OpenAI SDK interface.

## Outcome

- ✅ Impact: Created a complete skill for using OpenAI Agents SDK with multiple providers including Gemini
- 🧪 Tests: none
- 📁 Files: Created 4 files in the skill directory structure
- 🔁 Next prompts: Could enhance with more specific agent patterns or additional provider examples
- 🧠 Reflection: The OpenAI-compatible API design allows for flexible provider switching

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add Anthropic Claude integration example