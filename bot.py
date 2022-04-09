import discord
from discord.ext import commands
import json
import time

intents = discord.Intents.default()
intents.typing = True
intents.presences = True

bot = commands.Bot('>', intents=intents)
dm: discord.TextChannel = None
dup_fix = {}
status_duration = {}

@bot.event
async def on_ready():
    global dm
    await bot.change_presence(status=discord.Status.idle)
    dm = await bot.fetch_channel(962036905996853321)
    print('ready')

@bot.listen()
async def on_member_update(before: discord.Member, after: discord.Member):
    dup_fix[after.id] = dup_fix.get(after.id, after.guild.id)
    if dup_fix[after.id] != after.guild.id: return

    duration = round(time.time() - status_duration.get(after.id, time.time()+1))
    status_duration[after.id] = time.time()
    before_status = get_status_string(before)
    after_status = get_status_string(after)
    obf_name = after.display_name[:1] + after.display_name[-2:][::-1]
    obf_name = obf_name.lower()[::-1]
    if before_status != after_status:
        message = f"`{obf_name} {before_status}({round(duration/3600, 1)} hrs) >> {after_status}` <t:{int(time.time())}:R>"
        await dm.send(message)

def get_status_string(user: discord.Member) -> str:
    emojis = "   🔴  ⬛⚫"
    status = [discord.Status.online, discord.Status.dnd,
              discord.Status.idle, discord.Status.offline]
    status_index = status.index(user.status) * 2

    if not user.is_on_mobile():
        status_index += 1

    return emojis[status_index]


with open("token.json", "r") as f:
    token = json.load(f)["token"]

bot.run(token)