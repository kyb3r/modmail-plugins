import asyncio
import discord
from discord.ext import commands

from profanity_check import predict


class ProfanityFilter:
    def __init__(self, bot):
        self.bot = bot
        self.coll = bot.plugin_db.get_partition(self)
        self.enabled = True
        asyncio.create_task(self._set_config())

    async def _set_config(self):
        config = await self.coll.find_one({'_id': 'config'})
        self.enabled = config['enabled']

    @commands.command()
    @commands.is_owner()
    async def profanity(self, ctx, mode: bool):
        '''Disable or enable the profanity filter.
        
        Usage: `profanity enable` / `profanity disable` 
        '''
        self.enabled = mode

        await self.coll.update_one(
            {'_id': 'config'},
            {'$set': {'enabled': self.enabled}}, 
            upsert=True
            )
        
        await ctx.send('Enabled' if mode else 'Disabled' + ' the profanity filter.')
    
    async def on_message(self, message):
        if not self.enabled:
            return

        profane = bool(predict([message.content])[0])
        if not profane:
            return

        await message.delete()

        temp = await message.channel.send(
            f'{message.author.mention} your message has '
            'been deleted for containing profanity.'
            )
        
        await asyncio.sleep(5)
        await temp.delete()


def setup(bot):
    bot.add_cog(ProfanityFilter(bot))