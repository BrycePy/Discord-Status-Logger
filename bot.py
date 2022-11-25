import discord
from discord.ext import commands
import json
import time
import asyncio

intents = discord.Intents.default()
intents.typing = True
intents.presences = True

bot = commands.Bot('>', intents=intents)

log_channel: discord.TextChannel = None
sum_channel: discord.TextChannel = None
sum_channel_message: discord.Message = None

user_guild_table = {}
last_status_update = {}
last_active_text = {}

last_message_edit_ts = 0

with open("token.json", "r") as f:
    data = json.load(f)
    token = data["token"]
    log_channel_id = data["log_channel"]
    sum_channel_id = data["sum_channel"]

@bot.event
async def on_ready():
    global log_channel, sum_channel, sum_channel_message
    await bot.change_presence(status=discord.Status.idle)
    log_channel = await bot.fetch_channel(log_channel_id)
    sum_channel = await bot.fetch_channel(sum_channel_id)

    try:
        last_sum_message = await sum_channel.fetch_message(sum_channel.last_message_id)
        if last_sum_message.author.id == bot.user.id:
            sum_channel_message = last_sum_message
            await last_sum_message.edit(content="`starting up...`")
        else:
            raise discord.NotFound

    except discord.NotFound:
        sum_channel_message = await sum_channel.send("`starting up...`")
        
    print('Bot is ready.')

@bot.listen()
async def on_member_update(before: discord.Member, after: discord.Member):
    global last_message_edit_ts
    user_guild_table[after.id] = user_guild_table.get(after.id, after.guild.id)
    if user_guild_table[after.id] != after.guild.id: return

    status_update_time = last_status_update.get(after.id, time.time()+1)
    last_status_update[after.id] = time.time()
    duration = round(time.time() - status_update_time)
    duration_hr = round(duration/3600, 1)
    
    before_status = get_status_emoji(before)
    after_status = get_status_emoji(after)

    if before_status != after_status:
        message_sum = f"`{get_tag(after)}`\n`    {before_status}({duration_hr} hrs) >> {after_status}` <t:{int(time.time())}:R>"
        last_active_text[after.id] = (message_sum, after)
        # message = f"`{before_status}({duration_hr} hrs) >> {after_status}` <t:{int(time.time())}:R> `({get_tag(after)})`"
        # await log_channel.send(message)

    if last_message_edit_ts + 5 < time.time():
        last_message_edit_ts = time.time()
        await update_last_active()
    else:
        await asyncio.sleep(5)
        if last_message_edit_ts + 5 < time.time():
            await update_last_active()
    

async def update_last_active():
    buffer = ""
    for uid in sorted(last_active_text.keys(), key = lambda x: get_tag(last_active_text[x][1])):
        message, user = last_active_text[uid]
        buffer += f"{message}\n"

    if sum_channel_message:
        await sum_channel_message.edit(content=buffer)

def get_tag(user: discord.Member) -> str:
    return f"{user.name}#{user.discriminator}"

def get_status_emoji(user: discord.Member) -> str:
    emojis = "🟩🟢🟥🔴🟨🟡⬛⚫"
    status = [discord.Status.online, discord.Status.dnd,
              discord.Status.idle, discord.Status.offline]
    status_index = status.index(user.status) * 2

    if not user.is_on_mobile():
        status_index += 1

    return emojis[status_index]

bot.run(token)