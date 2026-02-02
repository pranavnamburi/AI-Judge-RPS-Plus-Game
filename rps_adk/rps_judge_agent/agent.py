# rps_judge_agent/agent.py
"""
RPS+Bomb Game - Prompt-Driven Architecture.

The LLM decides game outcomes using rules in the prompt.
Tools handle state I/O only (no game logic).
"""
import os
from google.adk.agents import LlmAgent
from google.adk.models import LiteLlm

from .tools import get_game_state, get_bot_move, commit_turn, reset_game
from .prompts_judge import JUDGE_SYSTEM_PROMPT, JUDGE_INSTRUCTION_PROMPT


# Model config
DEFAULT_MODEL = "gemini-2.5-flash"
MODEL_NAME = os.getenv("MODEL_NAME", DEFAULT_MODEL)


def create_model(name):
    """Create model - LiteLlm for external providers, string for Gemini."""
    if "/" in name:
        return LiteLlm(model=name)
    return name


MODEL = create_model(MODEL_NAME)


# The Judge Agent
# - Prompts contain ALL game rules
# - LLM decides winner (intent + game logic + response)
# - Tools only do state I/O
root_agent = LlmAgent(
    name="RPSJudge",
    model=MODEL,
    description="AI Judge for Rock-Paper-Scissors Plus. Evaluates moves and decides outcomes.",
    instruction=JUDGE_SYSTEM_PROMPT + "\n\n" + JUDGE_INSTRUCTION_PROMPT,
    tools=[
        get_game_state,   # Read current state
        get_bot_move,     # Get bot's choice (LLM call)
        commit_turn,      # Save round result
        reset_game,       # Start new game
    ],
)
