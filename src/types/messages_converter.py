import json
import typing as tp

import aiogram.types as at

from ..utils import parse_dice_output



def format_telegram_message(message: at.Message) -> str:
    result: dict[str, tp.Any] = dict()
    if (text := message.text) is not None:
        result['text'] = text
    if (dice := message.dice) is not None:
        result['text'] = dice.emoji
        result['system'] = parse_dice_output(dice.emoji, dice.value)
    if (new_chat_members := message.new_chat_members):
        result['users_joined'] = [
            {
                'full_name': user.full_name,
                'short_name': '@' + str(user.username),
            } for user in new_chat_members
        ]
    if (left_chat_member := message.left_chat_member) is not None:
        result['user_left'] = {
            'name': left_chat_member.full_name
        }

    return json.dumps(result)
