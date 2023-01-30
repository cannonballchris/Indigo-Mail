import discord
from discord.ext import commands


class Help(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	
	@commands.slash_command(name = "help", description = "✅ Shows all the information of commands.")
	async def help(self, ctx):
		help_embed = discord.Embed(title = "📜 Help Menu", description="ℹ️ Indigo Mail does not have too many commands since the bot is aimed at making things very simple. However, All the commands that are present are essential only.", color = 0x36393F)
		help_embed.add_field(name = "📥 Starter Commands", value = "> `/setup` - **This command sets up the ModMail feature in your server.**", inline = False)
		help_embed.add_field(name = "⚙️ Config Commands", value = "> `/disable` - **This command disables ModMail in your server. Can be useful if you have too many open threads and does not wish users to open new one.**", inline= False)
		help_embed.add_field(name = "👤 DM Commands", value = "> `/choose` - **This command is used to choose a thread where you wish to reply to. Can be useful if you have multiple server threads open!**", inline = False)
		help_embed.add_field(name = "🖌️ Utility Commands", value = "> `/anonymous` - **Toggle anonymous mode on or off for your reply to threads. This is useful if any staff member do not wish the users to know, to whom they are talking.**", inline = False)
		help_embed.add_field(name = "🗑️ Deletion Commands", value = "> `/close` - **This command is used to close a thread and send a transcript to the log channel.(Works in DM as well as Thread)**\n> `/reset` - **This command is used to reset ModMail in your server.**", inline = False)
		help_embed.add_field(name = "🔗 Links", value = "> [Support Server](https://discord.gg/cortexbotservices) | [Invite](https://ptb.discord.com/api/oauth2/authorize?client_id=1067744805607718962&permissions=498216594640&scope=applications.commands%20bot) | [Vote](https://top.gg/bot/937726571291238411/vote)", inline = False)
		await ctx.respond(embed = help_embed)

def setup(bot):
	bot.add_cog(Help(bot))