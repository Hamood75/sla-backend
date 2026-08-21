# AI-agent skills

This folder contains reusable instructions that an AI coding agent can follow when integrating Pay-IT into another application.

## Available skill

- [`payit-integration`](integration/SKILL.md) — interviews the user, defaults to the hosted checkout JavaScript SDK in modal mode unless another presentation or direct API initiation is explicitly required, assesses the target codebase and programming language, presents an implementation plan for explicit approval, implements the approved payment and webhook flows, verifies the result, and produces a deployment handoff.

## Using the skill

Give the `integration/` folder to an AI agent that supports `SKILL.md` instructions, or install/copy it into that agent's skills directory. Then ask the agent to use `payit-integration` and point it to the application that should be integrated.

The agent must begin with the integration interview in the skill. Do not paste live API keys, webhook secrets, or customer credentials into the conversation; make them available through the target application's secret-management mechanism.
