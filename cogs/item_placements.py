from discord.ext import commands


class ItemPlacements(commands.Cog, name='Item Placements'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='where-is', help='Reveals the location of a specified item.')
    async def where_is(self, ctx, *, item_name):
        try:
            response = '\n'.join(self.bot.spoiler_log.reveal_item_location(item_name))
        except KeyError:
            response = "Sorry, I don't know about that item. 😔 You might have mistyped it or searching for it might currently be disabled."
        except AttributeError:
            response = "Looks like you haven't uploaded a spoiler log file yet. 🤓 Try uploading one and then trying your command again."

        await ctx.send(response)

    @commands.command(name='all-items', help='Reveals all currently enabled item locations.')
    async def all_items(self, ctx):
        try:
            if (item_location_line_lists := self.bot.spoiler_log.reveal_all_item_locations()):
                responses = [
                    f'For the randomization with seed "{self.bot.spoiler_log.seed}", the key items can be found in the following locations:\n\n||' + \
                        '\n'.join(item_location_line_lists[0]) + '||'
                ]
                
                for item_location_line_list in item_location_line_lists[1:]:
                    responses.append('||' + '\n'.join(item_location_line_list) + '||')
            else:
                responses = ['No item locations are currently enabled.']
        except AttributeError:
            responses = ["Looks like you haven't uploaded a spoiler log file yet. 🤓 Try uploading one and then trying your command again."]

        for response in responses:
            await ctx.send(response)


async def setup(bot):
    await bot.add_cog(ItemPlacements(bot))
