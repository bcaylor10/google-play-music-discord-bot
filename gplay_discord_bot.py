import discord
from discord.ext import commands
#import asyncio

TOKEN = ''

bot = commands.Bot(command_prefix='.')

@bot.event
async def on_ready():
    print('Bot is ready...')

# @bot.event
# async def on_message_delete(message):
#     author = message.author
#     content = message.content
#     channel = message.channel

#     await bot.send_message(channel, '{}: {}'.format(author, content))

@bot.command()
async def ping():
    await bot.say('Pong!') #say can only be used in a command, send_message can be used in commands and events

@bot.command()
async def echo(*args):
    output = ''

    for word in args:
        output += word + ' '
    
    await bot.say(output)

@bot.command(pass_context=True)
async def clear(ctx, amount=100):
    channel = ctx.message.channel
    messages = []

    async for message in bot.logs_from(channel, limit=int(amount)):
        messages.append(message)

    await bot.delete_messages(messages)
    await bot.say(str(amount) + ' messages deleted.')



bot.run(TOKEN);

