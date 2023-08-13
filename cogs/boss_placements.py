from discord.ext import commands


class BossPlacements(commands.Cog, name='Boss Placements'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='who-replaces', help='Reveals the boss replacing a specified boss.')
    async def who_replaces(self, ctx, *, boss_name):
        try:
            response = self.bot.spoiler_log.reveal_boss_replacement(boss_name)
        except KeyError:
            response = "Sorry, I don't know about that boss. 😔 You might have mistyped it or searching for it might currently be disabled."
        except AttributeError:
            response = "Looks like you haven't uploaded a spoiler log file yet. 🤓 Try uploading one and then trying your command again."

        await ctx.send(response)

    @commands.command(name='major-bosses', help='Reveals the bosses replacing all major bosses.')
    async def major_bosses(self, ctx):
        try:
            if (boss_replacement_lines := self.bot.spoiler_log.reveal_major_boss_replacements()):            
                response = f'For the randomization with seed "{self.bot.spoiler_log.seed}", the following bosses have replaced the major bosses:\n\n||' + \
                    '\n'.join(boss_replacement_lines) + '||'
            else:
                response = 'Revealing boss replacements is currently disabled.'
        except AttributeError:
            response = "Looks like you haven't uploaded a spoiler log file yet. 🤓 Try uploading one and then trying your command again."

        await ctx.send(response)

    @commands.command(name='core-progression', help='Reveals the bosses replacing those guarding core progression.')
    async def core_progression(self, ctx):
        try:
            if (boss_replacement_lines := self.bot.spoiler_log.reveal_core_progression_boss_replacements()):            
                response = f'For the randomization with seed "{self.bot.spoiler_log.seed}", the following bosses have replaced those guarding core progression:\n\n||' + \
                    '\n'.join(boss_replacement_lines) + '||'
            else:
                response = 'Revealing boss replacements is currently disabled.'
        except AttributeError:
            response = "Looks like you haven't uploaded a spoiler log file yet. 🤓 Try uploading one and then trying your command again."

        await ctx.send(response)


async def setup(bot):
    await bot.add_cog(BossPlacements(bot))
