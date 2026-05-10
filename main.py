import asyncio
import os
import json
import typing as tp

from pathlib import Path

import click
import yaml  # type: ignore

from aiogram import Bot, Dispatcher, F
from google import genai as ga

from src.agent import GeminiAgent
from src.app import Application
from src.context import SQLiteChatContextManager
from src.logging import setup_logger
from src.tools import Tool, as_tool
from src.tools.telegram import write_to_chat, leave_chat, \
    make_sticker_tool, play_casino
from src.utils import dotdict


def read_yaml(p: str) -> dict:
    with open(p, 'r') as file:
        return yaml.safe_load(file)


def get_keys() -> dict[str, str]:
    return dotdict({
        'gemini': os.environ['GEMINI_API_KEY'],
        'telegram': os.environ['TELEGRAM_API_BOT_KEY'],
    })


def create_sticker_tool(stickers_file: str) -> Tool:
    config = read_yaml(stickers_file)
    data = [
        {
            'name': name,
            **value
        } for name, value in config.items()
    ]
    return make_sticker_tool(data)


def get_tools(stickers_file: str) -> list[Tool]:
    return [
        write_to_chat,
        leave_chat,
        play_casino,
        create_sticker_tool(stickers_file)
    ]


def tool_description_to_string(description: dict[str, tp.Any]) -> str:
    return json.dumps(description, indent=4)


async def build_system_prompt(bot: Bot, system_prompt_file: str) -> str:
    with open(system_prompt_file, 'r', encoding='utf-8') as file:
        content = file.read()

    me = await bot.me()
    return content.format(
        bot_username=me.full_name,
        bot_shortname=me.username,
    )


@click.command()
@click.option(
    '--system-prompt-file', type=click.Path(exists=True, dir_okay=False),
    default='config/system_prompt.txt',
    help='System prompt filepath'
)
@click.option(
    '--stickers-config-file', type=click.Path(exists=True, dir_okay=False),
    default='config/stickers.yaml',
    help='Stickers configuration filepath',
)
@click.option(
    '--config-file', type=click.Path(exists=True, dir_okay=False),
    default='config/config.yaml',
    help='Configuration filepath',
)
def sync_main(*args, **kwargs) -> None:
    asyncio.run(main(*args, **kwargs))


async def main(
    system_prompt_file: str,
    stickers_config_file: str,
    config_file: str,
) -> None:
    Path('logs').mkdir(exist_ok=True)

    config = read_yaml(config_file)
    keys = get_keys()

    bot = Bot(token=keys.telegram)
    dp = Dispatcher()

    context_manager = SQLiteChatContextManager(
        db_url=config['database']['url']
    )
    await context_manager.initialize_db()

    tools = get_tools(
        stickers_file=stickers_config_file
    )
    tools.append(as_tool(context_manager.update_context))

    print(f'Total: {len(tools)} tools')
    for tool in tools:
        print(tool_description_to_string(tool.description))

    agent = GeminiAgent(
        client=ga.Client(
            api_key=keys.gemini
        ),
        model_name=config['model']['name'],
        tools=tools,
        logger=setup_logger('agent', 'logs/agent.txt'),
        generation_config=config['generation_config'],
        concurrency_limit=config['app']['concurrency_limit'],
    )

    app = Application(
        bot=bot,
        system_prompt=await build_system_prompt(bot, system_prompt_file),
        context_manager=context_manager,
        agent=agent,
        messages_limit=config['app']['messages_context_limit'],
        logger=setup_logger('application', 'logs/application.txt')
    )

    dp.message(F.text)(app.message_handler)

    await dp.start_polling(bot)


if __name__ == '__main__':
    sync_main()
