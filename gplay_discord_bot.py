import discord
from discord.ext import commands
import asyncio
from itertools import cycle
import opuslib
from gmusicapi import Mobileclient
import youtube_dl
import random

TOKEN = 'NTU5MjA1ODIxNDQ4NDU0MTUz.D3iBXQ.ZfDZOR-ghxHq3dAtU5cMusNnqs8'

bot = commands.Bot(command_prefix='.')
bot.remove_command('help')

players = {}
queue = []
currentSong = []
songs = []


api = Mobileclient()
# api.perform_oauth(storage_filepath='mobileclient.cred', open_browser=True)
api.oauth_login(api.FROM_MAC_ADDRESS, '/Users/brandon/Desktop/discord-bot/mobileclient.cred')

library = api.get_all_songs()

#checks the queue and gets the next song if there is one
def check_queue(id):
    if queue != []:
        currentSong.append(queue[1])
        currentSong.pop(0)
        player = queue.pop(0)
        players[id] = player
        player.start()

#helper function to stop
def halt(id):
    if id in players:
        players[id].stop()
        players.pop(id)
            
    if id in queue:
        queue.pop(id)

#get the info of the current song
def getSongInfo():
    current = []

    for song in range(0, len(library)):
        if 'storeId' in library[song]:
            if str(currentSong[0]) == library[song]['storeId']:
                current.append(library[song])
                break

    title = str(current[0].get('title'))
    artist = str(current[0].get('artist'))

    return title, artist

#starts the bot
@bot.event
async def on_ready():
    print('Bot is running...')

#disconnect
@bot.command(pass_context=True)
async def disconnect(ctx):
    bot.close();

#clear messages
@bot.command(pass_context=True)
async def clear(ctx, amount=100):
    channel = ctx.message.channel
    messages = []

    async for message in bot.logs_from(channel, limit=int(amount)):
        messages.append(message)

    await bot.delete_messages(messages)
    await bot.say(str(amount) + ' messages deleted.')

#joining a voice channel
@bot.command(pass_context=True)
async def join(ctx):
    channel = ctx.message.author.voice.voice_channel
    try:
        await bot.join_voice_channel(channel)
    except:
        await bot.say("You're not in a voice channel, " + str(ctx.message.author.mention))

#leaving a voice channel
@bot.command(pass_context=True)
async def leave(ctx):
    server = ctx.message.server
    voice_client = bot.voice_client_in(server)

    if voice_client:
        await voice_client.disconnect()
    else:
        await bot.say("I must be in a voice channel before I can leave, " + str(ctx.message.author.mention))

#play
@bot.command(pass_context=True)
async def play(ctx):
    url = api.get_stream_url('Tnnxtonah7rm4isw7sumapx7r4y')
    server = ctx.message.server
    voice_client = bot.voice_client_in(server)
    channel = ctx.message.author.voice.voice_channel

    if voice_client:
        player = await voice_client.create_ytdl_player(url, after=lambda: check_queue(server.id))
        players[server.id] = player #adds server's player to dictionary
        player.start()
    else:
        if channel == None:
            await bot.say("You must be in a voice channel in order for me to play a song, " + str(ctx.message.author.mention))
        else:
            await bot.join_voice_channel(channel)

            server = ctx.message.server
            voice_client = bot.voice_client_in(server)

            player = await voice_client.create_ytdl_player(url, after=lambda: check_queue(server.id))
            players[server.id] = player #adds server's player to dictionary
            player.start()

#pause
@bot.command(pass_context=True)
async def pause(ctx):
    id = ctx.message.server.id
    players[id].pause()

#resume
@bot.command(pass_context=True)
async def resume(ctx):
    id = ctx.message.server.id
    players[id].resume()

#stop
@bot.command(pass_context=True)
async def stop(ctx):
    id = ctx.message.server.id
    halt(id)

#shuffle
@bot.command(pass_context=True)
async def shuffle(ctx):
    server = ctx.message.server
    voice_client = bot.voice_client_in(server)
    channel = ctx.message.author.voice.voice_channel

    songs = []

    for song in range(0, len(library)):
        songs.append(library[song].get('storeId'))

    random.shuffle(songs)
    url = api.get_stream_url(songs[0])
    currentSong.append(songs[0])

    if voice_client:
        
        halt(server.id)

        player = await voice_client.create_ytdl_player(url, after=lambda: check_queue(server.id))
        players[server.id] = player #adds server's player to dictionary

        for song in range(1, len(songs)):
            queue.append(songs[song])
        
        player.start()

        info = getSongInfo()

        await bot.say('Playing ' + info[0] + ' by ' + info[1])
        await bot.change_presence(game=discord.Game(name=''+info[0]+' by '+info[1], type=1))

    else:
        if channel == None:
            await bot.say("You must be in a voice channel in order for me to play a song, " + str(ctx.message.author.mention))
        else:
            halt(server.id)

            await bot.join_voice_channel(channel)

            server = ctx.message.server
            voice_client = bot.voice_client_in(server)

            player = await voice_client.create_ytdl_player(url, after=lambda: check_queue(server.id))
            players[server.id] = player #adds server's player to dictionary

            for song in range(1, len(songs)):
                queue.append(songs[song])

            player.start()

            info = getSongInfo()

            await bot.say('Playing ' + info[0] + ' by ' + info[1])
            await bot.change_presence(game=discord.Game(name=''+info[0]+' by '+info[1], type=1))

#troubleshooting function
@bot.command(pass_context=True)
async def check(ctx):
    server = ctx.message.server
    voice_client = bot.voice_client_in(server)
    channel = ctx.message.author.voice.voice_channel

    print('Checking Current Song ' + str(currentSong))
    print('Checking Current Queue ' + str(queue))

#goes to the next song
@bot.command(pass_context=True)
async def next(ctx):
    server = ctx.message.server
    voice_client = bot.voice_client_in(server)
    channel = ctx.message.author.voice.voice_channel

    # if server.id in queue:
    if len(queue) > 0:
        players[server.id].stop()
        players.pop(server.id)
        
        currentSong.append(queue[0])
        currentSong.pop(0)
        info = getSongInfo()
        queue.pop(0)

        url = api.get_stream_url(currentSong[0])

        player = await voice_client.create_ytdl_player(url, after=lambda: check_queue(server.id))
        players[server.id] = player #adds server's player to dictionary

        player.start()

        await bot.say('Playing `' + info[0] + ' by ' + info[1] + '`')
        await bot.change_presence(game=discord.Game(name=''+info[0]+' by '+info[1], type=1))
    else:
        await bot.say("There are no more songs in the queue, " + str(ctx.message.author.mention))

#help command
@bot.command(pass_context=True)
async def help(ctx):
    author = ctx.message.author

    msg = 'Hey there! Here is a list of the coommands you can give me and what they do :grin:'
    cmd1 = '```.shuffle: Shuffles the library and immediately plays music.'
    cmd2 = '.pause: Pauses the current player.'
    cmd3 = '.resume: Resumes the current player.'
    cmd4 = '.next: Skips the current song.'
    cmd5 = '.stop: Stops the current player.'
    cmd6 = '.join: Join current voice channel.'
    cmd7 = '.leave: Leave current voice channel.'
    cmd8 = '.clear: Clears the last 100 messages in any channel. However, inserting a space and any number greater than 0 will clear that many messages.```'

    message = '\n'.join([msg, cmd1, cmd2, cmd3, cmd4, cmd5, cmd6, cmd7, cmd8])

    await bot.send_message(author, str(message))

bot.run(TOKEN);