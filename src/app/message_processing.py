from datetime import datetime

from ..types import Message, ToolCallContext


def format_message(message: Message) -> str:
    return f'[{message.timestamp} {message.sender_name} ' \
        f'(@{message.sender_shortname}): {message.text}]'


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
        *[
            format_message(message)
            for message in previous_messages
        ],
        '## New messages',
        *[
            format_message(message)
            for message in new_messages
        ]
    ])
