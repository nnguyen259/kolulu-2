import os
from typing import Literal, Optional
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import find_dotenv, load_dotenv

from cogs.character import KoluluCharacter

if os.getenv("MODE") != "PROD":
    load_dotenv(find_dotenv(), verbose=True)

mappings = {
    "KoluluCharacter": KoluluCharacter,
}

MY_GUILD = discord.Object(id=os.getenv("MY_GUILD"))
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")


intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="k>>", intents=intents)
client.GUILD = MY_GUILD


@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("------")
    await client.load_extension("cogs.character")

    await client.tree.sync(guild=MY_GUILD)


@client.tree.command()
@app_commands.describe(module="Module to reload")
@commands.is_owner()
async def reload(interaction: discord.Interaction, module: Literal["character"]):
    print(f"Removing {module}")
    await client.reload_extension(f"cogs.{module}")
    await client.tree.sync(guild=MY_GUILD)
    await interaction.response.send_message(f"Reload {module} successfully")


@client.command()
@commands.is_owner()
async def sync(
    ctx: commands.Context,
    guilds: commands.Greedy[discord.Object],
    spec: Optional[Literal["~"]] = None,
) -> None:
    if not guilds:
        if spec == "~":
            fmt = await ctx.bot.tree.sync(guild=ctx.guild)
        else:
            fmt = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(fmt)} commands {'globally' if spec is not None else 'to the current guild.'}"
        )
        return

    assert guilds is not None
    fmt = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            fmt += 1

    await ctx.send(f"Synced the tree to {fmt}/{len(guilds)} guilds.")


client.run(DISCORD_TOKEN)
