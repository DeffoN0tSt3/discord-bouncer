import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Set up event listeners
@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

@bot.event
async def on_member_join(member):
    welcome_channel = discord.utils.get(member.guild.channels, name='welcome')
    await welcome_channel.send(f'Welcome, {member.mention}!')

@bot.event
async def on_member_remove(member):
    goodbye_channel = discord.utils.get(member.guild.channels, name='goodbye')
    await goodbye_channel.send(f'Goodbye, {member.mention}. We will miss you!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Check for toxic messages
    toxic_words = ['swearing', 'lgbtq+', 'racist', 'discriminatory', 'sexist', 'homophobic', 'transphobic', 'ableist', 'islamophobic', 'xenophobic', 'hate speech']
    if any(word in message.content.lower() for word in toxic_words):
        toxic_channel = discord.utils.get(message.guild.channels, name='toxicity-reports')
        await toxic_channel.send(f'{message.author.mention} has posted a toxic message in {message.channel.mention}:\n```\n{message.content}\n```')
        await message.channel.send(f'{message.author.mention} has been kicked for toxic behavior by the bouncer')
        await message.author.send('You have been kicked from the server for toxic behavior by the bouncer. Please review the server rules and try again later.')
        
        kick_channel = discord.utils.get(message.guild.channels, name='kick-notifications')
        await kick_channel.send(f'{message.author.mention} has been kicked for toxic behavior by the bouncer.')

        await message.author.kick(reason='Toxic behavior')

    await bot.process_commands(message)


# Command to report bullying
@bot.command(name='reportbouncer')
async def report(ctx, member: discord.Member, *, conversation):
    log_channel = discord.utils.get(ctx.guild.channels, name='log-channel')
    await log_channel.send(f'{ctx.author.mention} has reported {member.mention} for bullying. Here is the conversation:\n```{conversation}```')

# Kick inactive members
async def kick_inactive_members():
    await bot.wait_until_ready()
    while not bot.is_closed():
        inactive_time = 30  # days
        now = discord.utils.utcnow()
        for member in bot.get_all_members():
            if (now - member.joined_at).days >= inactive_time:
                inactive_channel = discord.utils.get(member.guild.channels, name='inactive-kicks')
                await inactive_channel.send(f'{member.mention} has been kicked for being inactive.')
                await member.send('You have been kicked from the server for being inactive by the bouncer. Please join again if you want to participate in the community, we miss you already!')
                await member.kick(reason='Inactive')
                await asyncio.sleep(1)  # avoid rate limiting

        await asyncio.sleep(24 * 60 * 60)  # check once a day

async def main():
    # Start the bot
    await bot.start('BOT_TOKEN')

# Run the main function using asyncio.run()
if __name__ == '__main__':
    asyncio.run(main())
