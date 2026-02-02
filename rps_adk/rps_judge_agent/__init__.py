# rps_judge_agent/__init__.py
"""
Rock-Paper-Scissors + Bomb game package.

This package implements a multi-agent RPS game using Google ADK.
The root_agent is a SequentialAgent that runs:
  1. BotPlayerAgent - chooses bot's move
  2. JudgeAgent - evaluates round and updates state

Exports:
    root_agent: The ADK entrypoint
"""
from .agent import root_agent

__all__ = ["root_agent"]
