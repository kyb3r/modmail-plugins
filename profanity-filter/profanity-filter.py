import discord
import asyncio
from profanity_check import predict


class ProfanityFilter:
    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
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