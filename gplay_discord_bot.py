import discord
import asyncio

client = discord.Client()

TOKEN = 'NTUxOTc2OTAwNzkzNDY2ODkx.D14-IA.nDeEtjj60niCOsGHMjOTmufG67g';

@client.event
async def on_ready():
    print('Bot is running...')

@client.event
async def on_message(message):
    if message.content.startswith('$play'):
        reply = message.content.replace('$play', '')
        await client.send_message(message.channel, 'Playing' + reply)
    elif message.content.startswith('$test'):
        reply = message.content.replace('$test', '')
        user = message.author.id
        channel = message.author.voice_channel
        if channel != None:
            await client.send_message(message.channel, 'Testing' + reply)
            await client.join_voice_channel(channel)
        else:
            await client.send_message(message.channel, 'You must be in a voice channel for me to work, dumbass.')


client.run(TOKEN);