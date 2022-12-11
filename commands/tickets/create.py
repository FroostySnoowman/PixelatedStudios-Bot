import discord
import aiosqlite
import yaml
from discord import app_commands
from discord.ext import commands

from buttons.tickets.tickets import TicketClose

with open('config.yml', 'r') as file:
    data = yaml.safe_load(file)

guild_id = data["General"]["GUILD_ID"]
embed_color = data["General"]["EMBED_COLOR"]
ticket_category_id = data["Tickets"]["TICKET_CATEGORY_ID"]
ticket_support_role_id = data["Tickets"]["TICKET_SUPPORT_ROLE_ID"]

class NewTicketCommandCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="new", description="Creates a new ticket!")
    @app_commands.guilds(discord.Object(id=guild_id))
    async def new(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message('The ticket is being created...', ephemeral=True)
        
        db = await aiosqlite.connect('database.db')

        category_channel = interaction.guild.get_channel(ticket_category_id)
        ticket_channel = await category_channel.create_text_channel(
            f"ticket-{interaction.user.name}")
        await ticket_channel.set_permissions(interaction.guild.get_role(interaction.guild.id),
                                         send_messages=False,
                                         read_messages=False)



        role = interaction.guild.get_role(ticket_support_role_id)
            
        await ticket_channel.set_permissions(role,
                                             send_messages=True,
                                             read_messages=True,
                                             add_reactions=True,
                                             embed_links=True,
                                             read_message_history=True,
                                             external_emojis=True)
        
        await ticket_channel.set_permissions(interaction.user,
                                         send_messages=True,
                                         read_messages=True,
                                         add_reactions=True,
                                         embed_links=True,
                                         attach_files=True,
                                         read_message_history=True,
                                         external_emojis=True)

        await db.execute('INSERT INTO tickets VALUES (?,?);', (interaction.user.id, ticket_channel.id))

        await db.commit()
        await db.close()

        await interaction.edit_original_response(content=f'The ticket has been created at {ticket_channel.mention}.')

        support_role = interaction.guild.get_role(ticket_support_role_id)

        x = support_role.mention

        view = TicketClose()
      
        embed=discord.Embed(title="", 
        description=f"""
A support member will be with you shortly!
""", 
        color=discord.Color.from_str(embed_color))

        await ticket_channel.send(content=x, embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(NewTicketCommandCog(bot), guilds=[discord.Object(id=guild_id)])