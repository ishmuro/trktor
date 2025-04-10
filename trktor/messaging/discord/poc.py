from typing import Optional

import discord
from discord.ext import commands


class DiscordBot(commands.Bot):
    def __init__(self, *args, test_guild: Optional[int] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_guild = test_guild
        intents = discord.Intents.default()
        intents.message_content = True