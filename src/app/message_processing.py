import json

from datetime import datetime

from ..types import Message, ToolCallContext


def format_message(message: Message) -> dict:
    if message.text[0] not in ['"', '{', ']']:
        content = message.text
    else:
        content = json.loads(message.text)
    return {
        'sender': message.sender_name,
        'sender_shortname': '@' + message.sender_shortname,
        'timestamp': str(message.timestamp),
        'content': content
    }


def prepare_input_prompt(
    new_messages: list[Message],
    previous_messages: list[Message],
    context: ToolCallContext,
) -> str:
    return '\n'.join([
        f'Time: {datetime.now()}',
        '## Chat context:',
        context.context or 'The context is empty. Use update_context tool to update it',
        '## Previous messages',
        json.dumps([
            format_message(message)
            for message in previous_messages
        ]),
        '## New messages',
        json.dumps([
            format_message(message)
            for message in new_messages
        ])
    ])
