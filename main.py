import discord
from discord.ext import commands
import asyncio

# Define constants
BOT_TOKEN = 'INSERT YOUR BOT TOKEN HERE'
COMMAND_PREFIX = '!'
# Add more words as desired below
TOXIC_WORDS = ['swearing', 'lgbtq+', 'racist', 'discriminatory', 'sexist', 'homophobic', 'transphobic', 'ableist', 'islamophobic', 'xenophobic', 'hate speech'] 
INACTIVE_TIME = 30  # in days

# Define channel names
WELCOME_CHANNEL_NAME = 'welcome'
GOODBYE_CHANNEL_NAME = 'goodbye'
TOXIC_CHANNEL_NAME = 'toxicity-reports'
KICK_NOTIFICATION_CHANNEL_NAME = 'kick-notifications'
LOG_CHANNEL_NAME = 'log-channel'
INACTIVE_CHANNEL_NAME = 'inactive-kicks'

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

# Set up event listeners
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_member_join(member):
    welcome_channel = discord.utils.get(member.guild.channels, name=WELCOME_CHANNEL_NAME)
    await welcome_channel.send(f'Welcome, {member.mention}!')

@bot.event
async def on_member_remove(member):
    goodbye_channel = discord.utils.get(member.guild.channels, name=GOODBYE_CHANNEL_NAME)
    await goodbye_channel.send(f'Goodbye, {member.mention}. We will miss you!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Check for toxic messages
    if any(word in message.content.lower() for word in TOXIC_WORDS):
        toxic_channel = discord.utils.get(message.guild.channels, name=TOXIC_CHANNEL_NAME)
        await toxic_channel.send(f'{message.author.mention} has posted a toxic message in {message.channel.mention}:\n```\n{message.content}\n```')
        await message.channel.send(f'{message.author.mention} has been kicked for toxic behavior.')
        await message.author.send('You have been kicked from the server for toxic behavior. Please review the server rules and try again later.')
        
        kick_channel = discord.utils.get(message.guild.channels, name=KICK_NOTIFICATION_CHANNEL_NAME)
        await kick_channel.send(f'{message.author.mention} has been kicked for toxic behavior.')

        await message.author.kick(reason='Toxic behavior')

    await bot.process_commands(message)

# Command to report bullying
@bot.command(name='reportbouncer')
async def report(ctx, member: discord.Member, *, conversation):
    log_channel = discord.utils.get(ctx.guild.channels, name=LOG_CHANNEL_NAME)
    await log_channel.send(f'{ctx.author.mention} has reported {member.mention} for bullying. Here is the conversation:\n```{conversation}```')

# Kick inactive members
async def kick_inactive_members():
    await bot.wait_until_ready()
    while not bot.is_closed():
        now = discord.utils.utcnow()
        for member in bot.get_all_members():
            if (now - member.joined_at).days >= INACTIVE_TIME:
                inactive_channel = discord.utils.get(member.guild.channels, name=INACTIVE_CHANNEL_NAME)
                await inactive_channel.send(f'{member.mention} has been kicked for being inactive.')
                await member.send('You have been kicked from the server for being inactive. Please join again if you want to participate.')
                await member.kick(reason='Inactive')
                await asyncio.sleep(1)  # avoid rate limiting

        await asyncio.sleep(24 * 60 * 60)  # check once a day

async def main():
    # Start the bot
    await bot.start('BOT_TOKEN')

# Run the main function using asyncio.run()
if __name__ == '__main__':
    asyncio.run(main())
