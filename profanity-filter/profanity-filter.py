import asyncio
import discord
from discord import Member, Role, TextChannel, DMChannel
from discord.ext import commands
from typing import Union

from profanity_check import predict


class ProfanityFilter:
    """
    A simple filter that checks for profanity in a message and 
    then deletes it. Many profanity detection libraries use a hard-coded 
    list of bad words to detect and filter profanity, however this 
    plugin utilises a library that uses a linear support vector machine 
    (SVM) model trained on 200k human-labeled samples of clean and profane 
    text strings. ([`profanity-check`](https://github.com/vzhou842/profanity-check)).

    Artificial intelligence in a discord bot? Heck yeah!
    """

    def __init__(self, bot):
        self.bot = bot
        self.coll = bot.plugin_db.get_partition(self)
        self.enabled = True
        self.whitelist = {
            'roles': [],
            'members': [],
            'text_channels': []
        }
        asyncio.create_task(self._set_config())

    async def _set_config(self):
        config = await self.coll.find_one({'_id': 'config'})
        self.enabled = config.get('enabled', True)
        self.whitelist = config.get('whitelist', self.whitelist)

    @commands.group()
    @commands.is_owner()
    async def profanity(self, ctx, mode: bool):
        """Disable or enable the profanity filter.
        
        Usage: `profanity enable` / `profanity disable` 
        """
        self.enabled = mode

        await self.coll.update_one(
            {'_id': 'config'},
            {'$set': {'enabled': self.enabled}}, 
            upsert=True
            )
        
        await ctx.send(('Enabled' if mode else 'Disabled') + ' the profanity filter.')
    
    @profanity.command()
    @commands.is_owner()
    async def whitelist(self, ctx, target: Union[Member, Role, TextChannel]):
        """Whitelist a user, role or channel from the profanity filter.
        
        Usage: `profanity whitelist @dude`
        """

        key = target.__class__.__name__.lower() + 's'

        if target.id in self.whitelist[key]:
            self.whitelist[key].remove(target.id)
            removed = True
        else:
            self.whitelist[key].append(target.id)
            removed = False

        await self.coll.update_one(
            {'_id': 'config'},
            {'$set': {'whitelist': self.whitelist}}, 
            upsert=True
            )
        
        await ctx.send(
            f"{'Un-w' if removed else 'W'}hitelisted "
            f"{target.mention} from the profanity filter."
            )

    
    async def on_message(self, message):

        if not self.enabled:
            return
        
        channel = message.channel
        author = message.author 

        if isinstance(channel, DMChannel):
            return

        if author.guild_permissions.administrator:
            return

        if any(r.id in self.whitelist['roles'] for r in author.roles):
            return
        
        if author.id in self.whitelist['members']:
            return

        if channel.id in self.whitelist['text_channels']:
            return

        profane = bool(predict([message.content])[0])
        if not profane:
            return

        await message.delete()

        temp = await channel.send(
            f'{author.mention} your message has '
            'been deleted for containing profanity.'
            )
        
        await asyncio.sleep(5)
        await temp.delete()


def setup(bot):
    bot.add_cog(ProfanityFilter(bot))