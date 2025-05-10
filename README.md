# Discord LLM Bot

A Discord bot that interfaces with [Ollama](https://ollama.com/) or [Koboldcpp](https://github.com/LostRuins/koboldcpp) to provide LLM-powered chat capabilities.

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

### Using with Ollama

4. Install Ollama from [ollama.com](https://ollama.com/)
5. Pull a model with Ollama:
   ```
   ollama pull llama3
   ```
6. Configure the `config.yaml` file if needed (set `type: "ollama"`)
7. Run the bot:
   ```
   python main.py
   ```

### Using with Koboldcpp

4. Install Koboldcpp from [GitHub](https://github.com/LostRuins/koboldcpp)
5. Run Koboldcpp with the OpenAI API enabled:
   ```
   ./koboldcpp.py --model path/to/your/model.gguf --listen --api-key yourpassword --oaiport 5001
   ```
   Note: `--api-key` is optional and can be omitted for passwordless access
6. Configure the `config.yaml` file for Koboldcpp:
   ```yaml
   llm:
     api:
       type: "koboldcpp"
       koboldcpp_url: "http://localhost:5001/v1"
       koboldcpp_api_key: "yourpassword"  # Leave empty if no password set
       koboldcpp_model: "llama3"  # The model you're running in Koboldcpp
   ```
7. Run the bot:
   ```
   python main.py
   ```
8. Test your Koboldcpp connection:
   ```
   python test_koboldcpp.py http://localhost:5001/v1 yourpassword
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
- Supports models from both Ollama and Koboldcpp

## Usage

- Tag the bot: `@BotName Hello there!`
- Reply to a message from the bot
- Use the `/help` command for more information

## Troubleshooting

If you have issues connecting to your LLM backend:

1. Make sure Ollama or Koboldcpp is installed and running
2. Verify the model exists in the backend
3. Check the connection with the appropriate test script:
   - For Ollama: `python test_llm_connection.py`
   - For Koboldcpp: `python test_koboldcpp.py`
4. Verify API URL and key in config.yaml