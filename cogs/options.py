from discord.ext import commands


class Options(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='enable-bell-bearings', help='Enables revealing of bell bearing locations.')
    async def enable_bell_bearings(self, ctx):
        self.bot.spoiler_log.reveal_bell_bearing_locations = True
        await ctx.send(f'Revealing of bell bearing locations enabled for randomization with seed "{self.bot.spoiler_log.seed}".')

    @commands.command(name='disable-bell-bearings', help='Disables revealing of bell bearing locations.')
    async def disable_bell_bearings(self, ctx):
        self.bot.spoiler_log.reveal_bell_bearing_locations = False
        await ctx.send(f'Revealing of bell bearing locations disabled for randomization with seed "{self.bot.spoiler_log.seed}".')

    @commands.command(name='enable-key-items', help='Enables revealing of key item locations.')
    async def enable_key_items(self, ctx):
        self.bot.spoiler_log.reveal_key_item_locations = True
        await ctx.send(f'Revealing of key item locations enabled for randomization with seed "{self.bot.spoiler_log.seed}".')

    @commands.command(name='disable-key-items', help='Disables revealing of key item locations.')
    async def disable_key_items(self, ctx):
        self.bot.spoiler_log.reveal_key_item_locations = False
        await ctx.send(f'Revealing of key item locations disabled for randomization with seed "{self.bot.spoiler_log.seed}".')

    @commands.command(name='enable-boss-replacements', help='Enables revealing of boss replacements.')
    async def enable_boss_replacements(self, ctx):
        self.bot.spoiler_log.reveal_boss_replacements = True
        await ctx.send(f'Revealing of major boss replacements enabled for randomization with seed "{self.bot.spoiler_log.seed}".')

    @commands.command(name='disable-boss-replacements', help='Disables revealing of boss replacements.')
    async def disable_boss_replacements(self, ctx):
        self.bot.spoiler_log.reveal_boss_replacements = False
        await ctx.send(f'Revealing of major boss replacements disabled for randomization with seed "{self.bot.spoiler_log.seed}".')


async def setup(bot):
    await bot.add_cog(Options(bot))
