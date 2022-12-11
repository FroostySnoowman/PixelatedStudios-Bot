import discord
import aiosqlite
import yaml
from discord import app_commands
from discord.ext import commands

from buttons.tickets.tickets import TicketSystem

with open('config.yml', 'r') as file:
    data = yaml.safe_load(file)

guild_id = data["General"]["GUILD_ID"]
embed_color = data["General"]["EMBED_COLOR"]

class TicketsCommandCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot.add_view(TicketSystem())

    @app_commands.command(name="panel", description="Sends the ticket panel!")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def panel(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(title="Tickets",
                              description="Click the buttons below to create a ticket!",
                              color=discord.Color.green())
        view = TicketSystem()
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message('Sent!', ephemeral=True)

    @app_commands.command(name="add", description="Adds someone to the ticket!")
    @app_commands.describe(member="Who do you want to add to the ticket?")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def add(self, interaction: discord.Interaction, member: discord.Member) -> None:
        db = await aiosqlite.connect('database.db')
        cursor = await db.execute('SELECT * from tickets WHERE channel_id=?', (interaction.channel.id, ))
        a = await cursor.fetchone()
        if a is None:
            embed = discord.Embed(title="ERROR",
                                  description="This is not a valid ticket channel!",
                                  color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.channel.set_permissions(member,
                                         send_messages=True,
                                         read_messages=True,
                                         add_reactions=True,
                                         embed_links=True,
                                         attach_files=True,
                                         read_message_history=True,
                                         external_emojis=True)
            await interaction.response.send_message(f'Added {member.mention} to the ticket!', ephemeral=True)

    @app_commands.command(name="remove", description="Removes someone from the ticket!")
    @app_commands.describe(member="Who do you want to remove from the ticket?")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def remove(self, interaction: discord.Interaction, member: discord.Member) -> None:
        db = await aiosqlite.connect('database.db')
        cursor = await db.execute('SELECT * from tickets WHERE channel_id=?', (interaction.channel.id, ))
        a = await cursor.fetchone()
        if a is None:
            embed = discord.Embed(title="ERROR",
                                  description="This is not a valid ticket channel!",
                                  color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.channel.set_permissions(member,
                                         send_messages=False,
                                         read_messages=False,
                                         add_reactions=False,
                                         embed_links=False,
                                         attach_files=False,
                                         read_message_history=False,
                                         external_emojis=False)
            await interaction.response.send_message(f'Removed {member.mention} from the ticket!', ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketsCommandCog(bot), guilds=[discord.Object(id=guild_id)])