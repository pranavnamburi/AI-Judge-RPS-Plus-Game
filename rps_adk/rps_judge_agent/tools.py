# rps_judge_agent/tools.py
"""
RPS+Bomb Game Tools - Pure State I/O.
NO game logic here - all decisions made by the LLM via prompts.
"""
from typing import Dict, Any
from google.adk.tools.tool_context import ToolContext
import os
from google import genai

# =============================================================================
# Constants
# =============================================================================
MAX_ROUNDS = 5
WIN_TARGET = 3
BOT_MODEL = os.getenv("BOT_MODEL", "gemini-2.5-flash")

# =============================================================================
# Default State
# =============================================================================
DEFAULTS = {
    "round": 1,
    "user_score": 0,
    "bot_score": 0,
    "draws": 0,
    "user_bomb_used": False,
    "bot_bomb_used": False,
    "game_over": False,
    "game_over_reason": "",
}


# =============================================================================
# Tool: Get Game State (Read-only)
# =============================================================================
def get_game_state(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Get the current game state. Returns all state values.
    
    This is a READ-ONLY tool - it does not modify state.
    Use commit_turn() to update state after each round.
    
    Returns:
        dict with: round, user_score, bot_score, draws,
                   user_bomb_used, bot_bomb_used, game_over, game_over_reason,
                   max_rounds, win_target
    """
    s = tool_context.state
    
    # Initialize defaults if needed
    for key, val in DEFAULTS.items():
        s.setdefault(key, val)
    
    return {
        "round": s["round"],
        "max_rounds": MAX_ROUNDS,
        "win_target": WIN_TARGET,
        "user_score": s["user_score"],
        "bot_score": s["bot_score"],
        "draws": s["draws"],
        "user_bomb_used": s["user_bomb_used"],
        "bot_bomb_used": s["bot_bomb_used"],
        "game_over": s["game_over"],
        "game_over_reason": s["game_over_reason"],
    }


# =============================================================================
# Tool: Get Bot Move (LLM-based, fair)
# =============================================================================
def get_bot_move(bot_bomb_used: bool) -> Dict[str, str]:
    """
    Get the bot's move via LLM. Called BEFORE seeing user's move (fair).
    
    Args:
        bot_bomb_used: True if bot has already used bomb this match
    
    Returns:
        dict with "move": rock/paper/scissors/bomb
    """
    try:
        client = genai.Client()
        prompt = f"""Pick ONE move for Rock-Paper-Scissors: rock, paper, scissors, or bomb.
Bomb beats everything but you can only use it ONCE per match.
Bomb available: {"YES" if not bot_bomb_used else "NO (already used)"}
Reply with ONLY the move name (rock, paper, scissors, or bomb). Nothing else."""
        
        response = client.models.generate_content(model=BOT_MODEL, contents=prompt)
        move = response.text.strip().lower()
        
        # Basic validation (no game logic, just format check)
        valid = ["rock", "paper", "scissors"]
        if not bot_bomb_used:
            valid.append("bomb")
        
        if move not in valid:
            move = "rock"  # fallback
        
        return {"move": move}
    except Exception as e:
        import random
        return {"move": random.choice(["rock", "paper", "scissors"])}


# =============================================================================
# Tool: Commit Turn (Write state + format output)
# =============================================================================
def commit_turn(
    user_move: str,
    bot_move: str,
    result: str,
    decision: str,
    explanation: str,
    user_score: int,
    bot_score: int,
    draws: int,
    user_bomb_used: bool,
    bot_bomb_used: bool,
    game_over: bool,
    game_over_reason: str,
    tool_context: ToolContext,
) -> Dict[str, str]:
    """
    Commit the round result to state and return formatted output.
    
    The LLM DECIDES the result, this tool just saves it.
    
    Args:
        user_move: What the user played (rock/paper/scissors/bomb/unclear)
        bot_move: What the bot played
        result: "user_win", "bot_win", "draw", or "wasted"
        decision: "VALID", "INVALID", or "UNCLEAR"
        explanation: Why this decision (e.g., "rock beats scissors")
        user_score: Updated user score
        bot_score: Updated bot score
        draws: Updated draw count
        user_bomb_used: Has user used bomb?
        bot_bomb_used: Has bot used bomb?
        game_over: Is the game over?
        game_over_reason: Why game is over
        tool_context: ADK context
    
    Returns:
        dict with "output": formatted round result string
    """
    s = tool_context.state
    current_round = s.get("round", 1)
    
    # Commit state
    s["round"] = current_round + 1
    s["user_score"] = user_score
    s["bot_score"] = bot_score
    s["draws"] = draws
    s["user_bomb_used"] = user_bomb_used
    s["bot_bomb_used"] = bot_bomb_used
    s["game_over"] = game_over
    s["game_over_reason"] = game_over_reason
    
    # Build output (formatting only, no logic)
    result_emoji = {
        "user_win": "You win! 🎉",
        "bot_win": "Bot wins! 🤖",
        "draw": "Draw! 🤝",
        "wasted": "Wasted turn ❌"
    }.get(result, result)
    
    lines = [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"Round {current_round}/{MAX_ROUNDS}",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"Your move: {user_move}",
        f"Bot move: {bot_move}",
        "",
        f"Decision: {decision}",
        f"Reason: {explanation}",
        f"Result: {result_emoji}",
        "",
        f"Score: You {user_score} | Bot {bot_score} | Draws {draws}",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]
    
    if game_over:
        lines.append(game_over_reason)
        lines.append('Type "reset" to play again.')
    else:
        bomb_note = ""
        if user_bomb_used:
            bomb_note = " (your bomb used)"
        lines.append(f"Next: rock, paper, scissors, or bomb{bomb_note}")
    
    output = "\n".join(lines)
    return {"status": "ok", "output": output}


# =============================================================================
# Tool: Reset Game
# =============================================================================
def reset_game(tool_context: ToolContext) -> Dict[str, str]:
    """
    Reset all game state to start a new match.
    
    Returns:
        dict with "output": new game message
    """
    s = tool_context.state
    for key, val in DEFAULTS.items():
        s[key] = val
    
    output = """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎮 NEW GAME STARTED!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
First to 3 wins, or highest score after 5 rounds.
Each player can use BOMB once (beats everything).

Type: rock, paper, scissors, or bomb"""

    return {"status": "ok", "output": output}
