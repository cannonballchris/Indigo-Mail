import discord
from discord.ext import commands


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, err):
        if isinstance(err, commands.MissingPermissions):
            perms = err.missing_permissions
            embed = discord.Embed(description = ":x: You are missing `"+ "`,`".join(perms)+"` to run this command.", color = discord.Color.brand_red())
            await ctx.respond(embed = embed)
        elif isinstance(err, commands.BotMissingPermissions):
            perms = err.missing_permissions
            embed = discord.Embed(description = ":x: I am missing `"+ "`,`".join(perms)+"` to run this command.", color = discord.Color.brand_red())
            await ctx.respond(embed = embed)
        else:
            raise err

def setup(bot):
    bot.add_cog(ErrorHandler(bot))