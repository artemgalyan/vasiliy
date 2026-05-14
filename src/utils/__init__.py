class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__  # type: ignore
    __delattr__ = dict.__delitem__  # type: ignore


def parse_slots(dice_value: int) -> tuple[str, bool, bool]:
    """
    Parses the casino slot machine values.
    Returns: (reel_string, is_max_win, is_any_three_match)
    """
    val = dice_value - 1
    symbols = ['➖', '🍇', '🍋', '7️⃣']

    reel_1 = val % 4           # Left reel
    reel_2 = (val // 4) % 4    # Middle reel
    reel_3 = (val // 16) % 4   # Right reel

    reel_str = ''.join([symbols[reel_1], symbols[reel_2], symbols[reel_3]])
    is_max_win = dice_value == 64  # Three 7s
    is_match = (reel_1 == reel_2 == reel_3)

    return reel_str, is_max_win, is_match


def parse_dice_output(emoji: str, value: int) -> str:
    """
    Parses the result of a dice/animated emoji throw.
    """
    if emoji in ["🎲", "🎯", "🏀"]:
        if not (1 <= value <= 6):
            return "Invalid value for standard dice/sport"
        return f"{emoji} result: {value}"

    elif emoji in ["⚽", "🎳"]:
        if not (1 <= value <= 5):
            return "Invalid value for football/bowling"

        outcomes = {
            "⚽": {1: "Miss", 2: "Post", 3: "Goal", 4: "Goal", 5: "Goal"},
            "🎳": {
                1: "Miss", 2: "1 Pin", 3: "Split", 4: "Near Strike",
                5: "Strike"
            }
        }

        return f"{emoji}: {outcomes[emoji].get(value)}"

    # 1-64 range: Slot Machine
    elif emoji == "🎰":
        if not (1 <= value <= 64):
            return "Invalid value for slots"

        reels, is_jackpot, is_match = parse_slots(value)
        return f"Slot Result: [{reels}]"

    return "Unknown emoji type"


__all__ = ['dotdict', 'parse_dice_output', 'parse_slots']
