import os
import asyncio
import platform
import ssl
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

from config import Config
from llm_interface import LLMInterface, Message

# SSL certificate workaround for macOS
if platform.system() == 'Darwin':
    # Create a custom SSL context that doesn't verify certificates
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Monkey patch the default create_default_context function
    original_create_default_context = ssl.create_default_context
    def patched_create_default_context(*args, **kwargs):
        context = original_create_default_context(*args, **kwargs)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context
    ssl.create_default_context = patched_create_default_context

# Initialize configuration
config = Config()

# Set up Discord intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guild_messages = True

# Initialize bot with command prefix
bot = commands.Bot(command_prefix=config.get_command_prefix(), intents=intents)

# Initialize LLM interface
llm_interface = LLMInterface(config)

@bot.event
async def on_ready():
    """Called when the bot is ready"""
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('---')
    
    # Sync commands
    try:
        await bot.tree.sync()
        print("Slash commands synced")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    
    # Set bot status
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening,
        name="your messages. Tag me to chat!"
    ))

@bot.event
async def on_message(message):
    """Called when a message is sent in a channel the bot can see"""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Process commands
    await bot.process_commands(message)
    
    # Check if this is a mention or reply to the bot
    is_mention = bot.user.mentioned_in(message) and not message.mention_everyone
    is_reply = message.reference and message.reference.resolved and message.reference.resolved.author == bot.user
    
    if is_mention or is_reply:
        await process_llm_query(message)

async def process_llm_query(message):
    """Process a message as an LLM query"""
    channel_id = str(message.channel.id)
    user_message = message.content
    
    # Remove mentions from the message
    for mention in message.mentions:
        user_message = user_message.replace(f'<@{mention.id}>', '')
        user_message = user_message.replace(f'<@!{mention.id}>', '')
    
    user_message = user_message.strip()
    
    if not user_message:
        # If the message is empty after removing mentions, ignore it
        return
    
    # Add typing indicator
    async with message.channel.typing():
        # Add user message to history
        llm_interface.add_message(channel_id, Message("user", user_message))
        
        # Query LLM
        response_text = llm_interface.query_llm(channel_id, user_message)
        
        # Split message if too long (Discord has a 2000 character limit)
        if len(response_text) > 2000:
            chunks = [response_text[i:i+1990] for i in range(0, len(response_text), 1990)]
            
            # Send each chunk
            for i, chunk in enumerate(chunks):
                if i == 0:
                    bot_message = await message.reply(chunk)
                else:
                    bot_message = await message.channel.send(chunk)
        else:
            # Send response
            bot_message = await message.reply(response_text)
        
        # Add bot response to history
        llm_interface.add_message(channel_id, Message("assistant", response_text))

@bot.tree.command(name="reset", description="Reset the conversation history with the bot")
async def reset_command(interaction: discord.Interaction):
    """Slash command to reset conversation history"""
    channel_id = str(interaction.channel_id)
    llm_interface.reset_conversation(channel_id)
    await interaction.response.send_message("Conversation history has been reset.", ephemeral=True)

@bot.tree.command(name="help", description="Get help with using the LLM bot")
async def help_command(interaction: discord.Interaction):
    """Slash command to show help information"""
    embed = discord.Embed(
        title="LLM Bot Help",
        description="I'm a bot that uses an LLM to chat with you!",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="How to Chat",
        value="To chat with me, either mention me in your message or reply to one of my messages.",
        inline=False
    )
    
    embed.add_field(
        name="Commands",
        value=f"`/reset` - Reset the conversation history\n"
              f"`/help` - Show this help message",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.command(name="ping")
async def ping_command(ctx):
    """Command to check if the bot is responsive"""
    latency = round(bot.latency * 1000)
    await ctx.send(f"Pong! Latency: {latency}ms")

if __name__ == "__main__":
    token = config.get_discord_token()
    if not token:
        print("Error: No Discord token provided in config or .env file")
    else:
        bot.run(token) 