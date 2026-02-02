# Rock-Paper-Scissors + Bomb 🎮💣

A **prompt-driven AI Judge** for Rock-Paper-Scissors Plus, built using **Google ADK**.

## What Makes This Special?

This project demonstrates **prompt-driven game logic**:

| Component | Location | Description |
|-----------|----------|-------------|
| Game Rules | **Prompts** | Rock beats scissors, bomb rules, etc. |
| Decision Making | **LLM** | Determines winner, validates moves |
| State I/O | **Python Tools** | Only reads/writes game state |

**The LLM is the judge** - it interprets rules and makes decisions. Python just handles storage.

---

## Game Rules

| Move | Beats |
|------|-------|
| ✊ Rock | ✌️ Scissors |
| ✌️ Scissors | 🖐️ Paper |
| 🖐️ Paper | ✊ Rock |
| 💣 Bomb | Everything! (once per match) |

- **Bomb vs Bomb** = Draw
- **Invalid/Unclear input** = Wasted turn
- **Win condition**: First to 3 wins OR highest score after 5 rounds

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    JudgeAgent (LLM)                         │
│                                                             │
│  PROMPTS contain:                                           │
│  • All game rules (rock > scissors, bomb rules, etc.)       │
│  • Move validation logic (VALID/INVALID/UNCLEAR)            │
│  • Winner determination logic                               │
│                                                             │
│  LLM's job:                                                 │
│  1. Intent Understanding - What did user try to do?         │
│  2. Game Logic - Apply rules, decide winner                 │
│  3. Response Generation - Explain the decision              │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Tools (Python)                           │
│                                                             │
│  • get_game_state() - Read current state                    │
│  • get_bot_move() - Get bot's random choice (LLM call)      │
│  • commit_turn() - Save round result to state               │
│  • reset_game() - Start new match                           │
│                                                             │
│  NO game logic here - just state I/O                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Why This Prompt Structure?

### 1. Rules in Prompts, Not Code
The assignment requires: *"Avoid hardcoding logic in code as much as possible"*

Game rules are in `prompts_judge.py`:
- Rock/paper/scissors win conditions
- Bomb beats everything (once per player)
- VALID/INVALID/UNCLEAR classification

### 2. Clean Separation of Concerns
The assignment requires: *"Clean separation of intent, game logic, response"*

- **Intent**: LLM parses user's free-text input
- **Game Logic**: LLM applies rules from prompt
- **Response**: LLM generates explanation + calls commit_turn()

### 3. Explainability
The assignment requires: *"Ability to explain decisions"*

Every round includes:
- Decision: VALID / INVALID / UNCLEAR
- Reason: "rock beats scissors" or "bomb already used"

---

## Failure Cases Considered

| Scenario | How Handled |
|----------|-------------|
| Typos (`rcok`) | LLM marks as UNCLEAR, wasted turn |
| Ambiguous (`maybe rock`) | UNCLEAR, wasted turn |
| Multiple moves (`rock or paper`) | UNCLEAR, wasted turn |
| Bomb used twice | INVALID, wasted turn |
| Bot tries bomb twice | Validated in get_bot_move() |
| Empty input | UNCLEAR, wasted turn |
| LLM hallucination | Rare with Gemini 2.5; fallback in tools |

---

## What I Would Improve Next

1. **Structured Output**: Use ADK's `output_schema` to force JSON responses, reducing format variability
2. **Match History**: Log past rounds for context
3. **Difficulty Levels**: Different bot strategies (defensive, aggressive)
4. **Test Suite**: Automated tests for edge cases
5. **Multi-language**: i18n support for prompts

---

## Project Structure

```
rps_adk/
├── rps_judge_agent/
│   ├── __init__.py         # Exports root_agent
│   ├── agent.py            # JudgeAgent setup
│   ├── tools.py            # State I/O tools (no logic)
│   ├── prompts_judge.py    # ALL game rules here
│   └── .env                # API key config
├── requirements.txt
└── README.md
```

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key in .env
echo "GOOGLE_API_KEY=your_key" > rps_judge_agent/.env

# Run the game
adk run rps_judge_agent
```

---

## Example Session

```
[user]: rock
[RPSJudge]: ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Round 1/5
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Your move: rock
Bot move: scissors

Decision: VALID
Reason: rock beats scissors
Result: You win! 🎉

Score: You 1 | Bot 0 | Draws 0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Next: rock, paper, scissors, or bomb
```

---

## License

MIT
