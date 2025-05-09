# Discord LLM Bot

A Discord bot that interfaces with [Ollama](https://ollama.com/) to provide LLM-powered chat capabilities.

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your Discord bot token:
   ```
   DISCORD_TOKEN=your_discord_bot_token
   ```
4. Install Ollama from [ollama.com](https://ollama.com/)
5. Pull a model with Ollama:
   ```
   ollama pull llama3
   ```
6. Configure the `config.yaml` file if needed (e.g., to change model)
7. Run the bot:
   ```
   python main.py
   ```

### SSL Certificate Issue on macOS

If you encounter SSL certificate verification errors on macOS, you have two options:

1. **Use the built-in workaround**: The code includes a workaround for macOS SSL certificate issues.

2. **Fix the certificates properly**:
   - Run the included helper script: `python install_certificates.py`
   - Or manually run: `/Applications/Python 3.X/Install Certificates.command`
   - If needed, install the certifi package: `pip install certifi`

## Features

- Chat with an LLM by tagging the bot or replying to its messages
- Configurable bot personality via character.json
- Supports all models available in Ollama

## Usage

- Tag the bot: `@BotName Hello there!`
- Reply to a message from the bot
- Use the `/help` command for more information

## Troubleshooting

If you have issues connecting to Ollama:

1. Make sure Ollama is installed and running
2. Verify the model exists in Ollama with `ollama list`  
3. Check the connection with `python test_llm_connection.py` 