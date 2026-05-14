# Vasiliy 2.0

This project is an example of a telegram chatbot based on agentic AI. Make sure to have some fun with the bot! You are very welcome to contribute to the project!

# Installation guide

1. Install ```uv```
2. Run ```uv sync``` in the repo root
3. Obtain Gemini API and Telegram API keys. Set environment variables ```GEMINI_API_KEY``` and ```TELEGRAM_API_BOT_KEY```:
```bash
export GEMINI_API_KEY=<YOUR GEMINI API KEY>
export TELEGRAM_API_BOT_KEY=<YOUR TELEGRAM BOT API KEY>
```
4. Optional: setup prometheus port in [config/config.yaml](config/config.yaml)
5. Run the bot: ```uv run main.py```

You can use ```--no-prometheus-flag``` to disable prometheus logging.

# Configuration files

All the configuration files (including prompt) are located in the [config](config/) directory. Feel free to experiment with prompts and parameters.

# Q&A

## How to change personality?

Go to the [config/system_prompt.txt](config/system_prompt.txt) and change the paragraph with personality. If you want to create a separate file for your personality, you can pass it on launch via ```--system-prompt-file <PATH TO THE FILE>``` flag.

Do not hardcode bot username and shortname into the prompt file - it will be subsituted automatically on the launch.

## How to add more stickers to the bot?

1. Obtain ```file_id``` for the sticker
2. Make up a name for the sticker. It should be quite informative for the bot because it chooses stickers only based on the provided text. For example: ```i_do_not_want_to_talk_right_now```
3. Add the following text to the [config/stickers.yaml](config/stickers.yaml):

```
<YOUR STICKER NAME>:
  id: <YOUR STICKER FILE ID>
```

## How to make my bot see and answer other bots messages?

1. Go to [@BotFather](https://t.me/BotFather)
2. Enable bot2bot with ```/setbot2bot```

## How can I change the model?

If you want to use one of Gemini models, change the ```model_name``` in the [config/config.yaml](config/config.yaml). Do not forget to change pricing fields if you want to monitor money spending in the prometheus!

If you want to use other models, you will have to implement ```src.agent.Agent``` for your model.

## Why 2.0?

This is the second version of the chatbot. The first version used chatting LLM for the bot. New version has lots of new features and is more fun!