# Vasiliy 2.0

This project is an example of a telegram chatbot based on agentic AI. Make sure to have some fun with the bot!

# Installation guide

1. Install ```uv```
2. Run ```uv sync``` in the repo root
3. Obtain Gemini API and Telegram API keys. Set environment variables GEMINI_API_KEY and TELEGRAM_API_BOT_KEY:
```bash
export GEMINI_API_KEY=<YOUR GEMINI API KEY>
export TELEGRAM_API_BOT_KEY=<YOUR TELEGRAM BOT API KEY>
```
4. Run the bot: ```uv run main.py```

# Configuration files

All the configuration files (including prompt) are located in the [config](config/) directory. Feel free to experiment with prompts and parameters.