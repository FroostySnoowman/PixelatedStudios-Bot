import discord
import asyncio
import aiosqlite
import yaml
from discord.ext.commands import CommandNotFound
from discord.ext import commands

with open('config.yml', 'r') as file:
    data = yaml.safe_load(file)

guild_id = data["General"]["GUILD_ID"]
token = data["General"]["TOKEN"]

intents = discord.Intents.all()
intents.message_content = True

initial_extensions = [
                      'buttons.tickets.tickets',
                      'commands.tickets.create',
                      'commands.tickets.tickets'
                      ]

playing = discord.Game(name="Creating Tickets!")
class TicketBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('.'), owner_id=503641822141349888, intents=intents, activity=playing, status=discord.Status.online)
        self.persistent_views_added = False

    async def on_ready(self):

        print(f'Signed in as {self.user}')

        await self.tree.sync(guild=discord.Object(id=guild_id))
        await self.tree.sync()

    async def setup_hook(self):
        for extension in initial_extensions:
            await self.load_extension(extension)

client = TicketBot()
client.remove_command('help')

@client.command()
@commands.is_owner()
async def sqlite(ctx):
    db = await aiosqlite.connect('database.db')
    cursor = await db.execute("""
   CREATE TABLE tickets (
        user_id INTEGER,
        channel_id INTEGER
    )""")
    await cursor.close()
    await db.commit()
    await db.close()
    a = await ctx.reply('Done!')
    await asyncio.sleep(5)
    await a.delete()
    await ctx.message.delete()

@client.command()
@commands.is_owner()
async def delete(ctx):
    db = await aiosqlite.connect('database.db')
    await db.execute('DROP TABLE tickets;')
    await db.commit()
    await db.close()
    a = await ctx.reply('Done!')
    await asyncio.sleep(5)
    await ctx.message.delete()
    await a.delete()

#\\\\\\\\\\\\Error Handler////////////
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error

client.run(token)