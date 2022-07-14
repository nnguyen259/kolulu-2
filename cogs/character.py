import json
import os
from typing import Any, Dict, List, Tuple

import discord
from discord import app_commands
from discord.ext import commands
from thefuzz import fuzz, process


class KoluluCharacter(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        super().__init__()
        self.client = client
        self.characters_data, self.characters_id = self.load_characters()

    def load_characters(self) -> Tuple[Dict[str, Any], Dict[str, str]]:
        with open("SSRs.json", encoding="utf-8") as ssr_file, open(
            "NameAndID.json", encoding="utf-8"
        ) as name_file:
            characters = json.load(name_file)
            data = json.load(ssr_file)
        return data, characters

    async def char_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        names = self.characters_id.keys()
        output = process.extractBests(current, names, scorer=fuzz.partial_ratio)
        return [
            app_commands.Choice(name=f"{name[1]} - {name[0]}", value=name[0])
            for name in output
        ]

    @app_commands.command()
    @app_commands.describe(character="Character to look up")
    @app_commands.autocomplete(character=char_autocomplete)
    async def gbfchar(self, interaction: discord.Interaction, character: str):
        """Who's that character?"""
        await interaction.response.send_message(
            f"Hi, {interaction.user.mention}, your character is {character}",
            ephemeral=True,
        )

    @app_commands.command()
    @app_commands.guilds(os.getenv("MY_GUILD"))
    @commands.is_owner()
    async def charreload(self, interaction: discord.Interaction):
        """Data reload"""
        self.characters_data, self.characters_id = self.load_characters()
        await interaction.response.send_message(
            f"Data reloaded",
            ephemeral=True,
        )


async def setup(client: commands.Bot):
    await client.add_cog(KoluluCharacter(client), guild=client.GUILD)
