import discord
from discord.ext import commands
import aiosqlite
from asyncio import sleep
from discord.ui import Button, View

async def create_modmail(self, ctx):
    
    embed = discord.Embed(title = "⚙️ ModMail Setup", description = "✉️ Modmail is a service where user direct messages the bot, and the bot creates a channel for staff to communicate to them via the bot. The bot is aimed at making that easier, and more efficient.\n\n ⌛ Starting the setup in your server...", color = 0x95bb72)
    embed.set_footer(text = f"Setup initiated by {ctx.author.name}", icon_url = ctx.guild.icon.url if ctx.guild.icon else self.bot.user.avatar.url)
    await ctx.respond(embed = embed)
    await sleep(2)
    category = await ctx.guild.create_category("ModMail", reason = f"ModMail setup carried out by {ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id})")
    await category.set_permissions(ctx.guild.me, read_messages = True, send_messages = True, manage_channels = True)
    await category.set_permissions(ctx.guild.default_role, read_messages = False, send_messages = False)

    category_id = category.id
    #Create a log channel for the bot to log messages in that category
    await sleep(1)
    log_channel = await ctx.guild.create_text_channel("modmail-logs", category = category, reason = f"ModMail setup carried out by {ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id})")
    log_channel_id = log_channel.id
    log_welcome_embed = discord.Embed(title = "📝 ModMail Logs", description = "ℹ️ This channel is setup to send modmail logs such as create logs, delete, transcripts etc.", color = 0xefd033)
    log_welcome_embed.set_footer(text = f"Setup initiated by {ctx.author.name}", icon_url = ctx.guild.icon.url if ctx.guild.icon else self.bot.user.avatar.url)
    await log_channel.send(embed = log_welcome_embed)
    async with self.db.cursor() as cursor:
        await cursor.execute("INSERT INTO setup VALUES(?, ?, ?, ?)", (ctx.guild.id, category_id, log_channel_id, 1))
        await self.db.commit()


class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        setattr(self, "db", await aiosqlite.connect("./Database/setup.db"))
        setattr(self, "threads", await aiosqlite.connect("./Database/threads.db"))
        setattr(self, "users", await aiosqlite.connect("./Database/user.db"))
        await sleep(2)
        async with self.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS setup(guild_id INTEGER, category_id INTEGER, log_channel INTEGER, enabled BOOL)")
        


    @commands.slash_command(name = "setup", description = "⚙️ Setup modmail in your server!")
    @commands.has_permissions(manage_guild = True)
    @commands.bot_has_guild_permissions(manage_channels = True, manage_roles = True)
    async def setup(self, ctx):
        await ctx.defer()
        async with self.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM setup WHERE guild_id = ?", (ctx.guild.id,))
            if await cursor.fetchone():
                already_exist_embed = discord.Embed(title = "⚠️ Setup already exists", description = "It seems like you have already setup your server. If you want to reinitiate your setup, please click on the reset button below ⬇️", color = 0xf01e2c)
                button1 = Button(
                    style = discord.ButtonStyle.danger,
                    label = "Reset",
                    emoji = "🔄"
                )
                view = View()
                view.add_item(button1)
                async def btn1callback(interaction:discord.Interaction):

                    reset_embed = discord.Embed(title = "✅ Reset successful", description = "ℹ️ The **configuration** setup was reset for your server.", color = 0xffb933)
                    await interaction.response.edit_message(embed= reset_embed,view = None)
                    async with self.db.cursor() as cursor:
                        await cursor.execute("DELETE FROM setup WHERE guild_id = ?", (ctx.guild.id,))
                        await self.db.commit()
                    await create_modmail(self, ctx)
                button1.callback = btn1callback
                await ctx.respond(embed = already_exist_embed, view = view)
                
                return
            await create_modmail(self, ctx)


    @commands.slash_command(name = "reset", description = "🔄 Reset ModMail in your server.")
    @commands.has_guild_permissions(manage_guild = True)
    async def reset_cmd(self, ctx):
        await ctx.defer()
        async with self.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM setup WHERE guild_id = ?", (ctx.guild.id,))
            if not await cursor.fetchone():
                no_setup_error = discord.Embed(title = "❓No setup found", description=":x: No setup for ModMail was found in this server. Therefore, nothing changed.\n ℹ️ Incase you wish to setup one for your server, use `/setup` to setup the system!", color = 0xf01e2c)
                await ctx.respond(embed = no_setup_error)
            else:
                await cursor.execute("DELETE FROM setup WHERE guild_id = ?", (ctx.guild.id,))
                await self.db.commit()
                async with self.threads.cursor() as cursor1:
                    await cursor1.execute("SELECT * FROM threads WHERE guild_id = ?", (ctx.guild.id,))
                    if await cursor1.fetchone():
                        await cursor1.execute("DELETE FROM threads WHERE guild_id = ?", (ctx.guild.id,))
                        await self.threads.commit()
                async with self.users.cursor() as cursor2:
                    await cursor2.execute("SELECT * FROM users WHERE guild_id = ?", (ctx.guild.id,))
                    if await cursor2.fetchone():
                        await cursor2.execute("DELETE FROM users WHERE guild_id = ?", (ctx.guild.id,))
                        await self.users.commit()
                successful_delete_embed = discord.Embed(title = "🔄 Modmail reset", description="🗑️ The configuration of modmail was successful. The bot will no longer accept any modmails for this server.\n ℹ️ You will be required to delete the thread channels for current threads.However, this will not send the transcript in the logs channel anymore.", color = 0x95bb72)
                successful_delete_embed.set_footer(text=f"Reset requested by: {ctx.author.name}#{ctx.author.discriminator}")
                await ctx.respond(embed = successful_delete_embed)

    @commands.slash_command(name = "disable", description = "🔒 Disable ModMail in your server.")
    @commands.has_guild_permissions(manage_guild = True)
    async def disable_cmd(self, ctx):
        await ctx.defer()
        async with self.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM setup WHERE guild_id = ?", (ctx.guild.id,))
            retrieved_data = await cursor.fetchone()
            if not retrieved_data:
                no_setup_error = discord.Embed(title = "❓No setup found", description=":x: No setup for ModMail was found in this server. Therefore, nothing changed.\n ℹ️ Incase you wish to setup one for your server, use `/setup` to setup the system!", color = 0xf01e2c)
                await ctx.respond(embed = no_setup_error)
            else:
                if retrieved_data[3] == 0:
                    val = 1
                else:
                    val = 0
                await cursor.execute("UPDATE setup SET enabled = ? WHERE guild_id = ?", (val, ctx.guild.id,))
                await self.db.commit()
                successful_delete_embed = discord.Embed(title = "🔒 Modmail disabled", description="🔒 The configuration of modmail was successful. The bot will no longer accept any modmails for this server.\n ℹ️ You will be required to delete the thread channels for current threads.However, this will not send the transcript in the logs channel anymore.", color = 0x95bb72)
                successful_delete_embed.set_footer(text=f"Disabled requested by: {ctx.author.name}#{ctx.author.discriminator}")
                await ctx.respond(embed = successful_delete_embed)
    
def setup(bot):
    bot.add_cog(Setup(bot))
