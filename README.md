# Discord LLM Bot

A Discord bot that interfaces with an LLM hosted via an OpenAI-compatible API (like Ollama or KoboldCPP).

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your Discord bot token and other configuration:
   ```
   DISCORD_TOKEN=your_discord_bot_token
   ```
4. Configure the `config.yaml` file with your LLM API settings
5. Run the bot:
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
- Configurable LLM endpoint (Ollama, KoboldCPP, etc.)
- Customizable bot personality via character.json

## Usage

- Tag the bot: `@BotName Hello there!`
- Reply to a message from the bot
- Use the `/help` command for more information 