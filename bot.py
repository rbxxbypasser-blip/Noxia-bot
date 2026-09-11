import discord
import asyncio
from discord import app_commands
from discord.ext import commands
import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


config = load_config()


# ═══════════════════════════════════════
# ✨ FANCY URL BUTTONS
# ═══════════════════════════════════════

class FancyButtons(discord.ui.View):
    def __init__(self, buttons):
        super().__init__(timeout=None)

        for label, url, emoji in buttons:
            self.add_item(
                discord.ui.Button(
                    label=label,
                    url=url,
                    emoji=emoji,
                    style=discord.ButtonStyle.link
                )
            )


# ═══════════════════════════════════════
# 👋 WELCOME SYSTEM
# ═══════════════════════════════════════

class WelcomeGroup(app_commands.Group):
    def __init__(self):
        super().__init__(
            name="welcome",
            description="Manage the welcome system."
        )

    @app_commands.command(
        name="setup",
        description="Set up the welcome channel."
    )
    @app_commands.describe(
        channel="The channel for welcome messages."
    )
    async def setup(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ You need **Manage Server** permission.",
                ephemeral=True
            )
            return

        guild_id = str(interaction.guild.id)

        config.setdefault(guild_id, {})
        config[guild_id]["welcome"] = {
            "enabled": True,
            "channel": channel.id,
            "message": "✨ Welcome {user} to **{server}**! You are member #{member_count}."
        }

        save_config(config)

        await interaction.response.send_message(
            f"╭・✨ **𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐒𝐞𝐭𝐮𝐩**\n"
            f"╰・📍 Channel: {channel.mention}\n"
            f"╰・🟢 Status: **Enabled**",
            ephemeral=True
        )

    @app_commands.command(
        name="message",
        description="Change the welcome message."
    )
    @app_commands.describe(
        message="Your welcome message."
    )
    async def message(
        self,
        interaction: discord.Interaction,
        message: str
    ):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ You need **Manage Server** permission.",
                ephemeral=True
            )
            return

        guild_id = str(interaction.guild.id)

        if guild_id not in config or "welcome" not in config[guild_id]:
            await interaction.response.send_message(
                "❌ Run `/welcome setup` first.",
                ephemeral=True
            )
            return

        config[guild_id]["welcome"]["message"] = message
        save_config(config)

        await interaction.response.send_message(
            "✨ **𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐦𝐞𝐬𝐬𝐚𝐠𝐞 𝐮𝐩𝐝𝐚𝐭𝐞𝐝!**",
            ephemeral=True
        )

    @app_commands.command(
        name="test",
        description="Test the welcome message."
    )
    async def test(self, interaction: discord.Interaction):

        guild_id = str(interaction.guild.id)
        welcome = config.get(guild_id, {}).get("welcome")

        if not welcome:
            await interaction.response.send_message(
                "❌ Run `/welcome setup` first.",
                ephemeral=True
            )
            return

        channel = interaction.guild.get_channel(
            welcome["channel"]
        )

        if not channel:
            await interaction.response.send_message(
                "❌ Welcome channel no longer exists.",
                ephemeral=True
            )
            return

        message = welcome["message"].format(
            user=interaction.user.mention,
            server=interaction.guild.name,
            member_count=interaction.guild.member_count
        )

        embed = discord.Embed(
            title="╭・✨ 𝐖𝐞𝐥𝐜𝐨𝐦𝐞!",
            description=message,
            color=discord.Color.blurple()
        )

        embed.set_thumbnail(
            url=interaction.user.display_avatar.url
        )

        embed.set_footer(
            text="𝐍𝐨𝐱𝐢𝐚 ♡ • Welcome System"
        )

        embed.timestamp = discord.utils.utcnow()

        await channel.send(embed=embed)

        await interaction.response.send_message(
            "✨ **Test welcome sent!**",
            ephemeral=True
        )

    @app_commands.command(
        name="disable",
        description="Disable the welcome system."
    )
    async def disable(self, interaction: discord.Interaction):

        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ You need **Manage Server** permission.",
                ephemeral=True
            )
            return

        guild_id = str(interaction.guild.id)

        if guild_id in config and "welcome" in config[guild_id]:
            config[guild_id]["welcome"]["enabled"] = False
            save_config(config)

        await interaction.response.send_message(
            "🔕 **𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐬𝐲𝐬𝐭𝐞𝐦 𝐝𝐢𝐬𝐚𝐛𝐥𝐞𝐝.**",
            ephemeral=True
        )

    @app_commands.command(
        name="config",
        description="View welcome settings."
    )
    async def show_config(self, interaction: discord.Interaction):

        guild_id = str(interaction.guild.id)
        welcome = config.get(guild_id, {}).get("welcome")

        if not welcome:
            await interaction.response.send_message(
                "❌ Welcome system is not configured.",
                ephemeral=True
            )
            return

        channel = interaction.guild.get_channel(
            welcome["channel"]
        )

        embed = discord.Embed(
            title="╭・⚙️ 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐒𝐞𝐭𝐭𝐢𝐧𝐠𝐬",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="📍 𝐂𝐡𝐚𝐧𝐧𝐞𝐥",
            value=channel.mention if channel else "Deleted",
            inline=False
        )

        embed.add_field(
            name="🔘 𝐒𝐭𝐚𝐭𝐮𝐬",
            value="🟢 **Enabled**" if welcome["enabled"]
            else "🔴 **Disabled**",
            inline=False
        )

        embed.set_footer(
            text="𝐍𝐨𝐱𝐢𝐚 ♡ • Configuration"
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


# ═══════════════════════════════════════
# 💎 FANCY EMBED SYSTEM
# ═══════════════════════════════════════

class EmbedGroup(app_commands.Group):
    def __init__(self):
        super().__init__(
            name="embed",
            description="Create premium fancy embeds."
        )

    @app_commands.command(
        name="setup",
        description="Create a premium fancy embed."
    )
    @app_commands.describe(
        channel="Channel where the embed will be sent.",
        title="Main embed title.",
        description="Main embed description.",
        thumbnail="Thumbnail image URL.",
        image="Large image URL.",
        button1="First button name.",
        url1="First button URL.",
        button2="Second button name.",
        url2="Second button URL.",
        button3="Third button name.",
        url3="Third button URL."
    )
    async def setup(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        title: str,
        description: str,
        thumbnail: str = "",
        image: str = "",
        button1: str = "🌐 Website",
        url1: str = "",
        button2: str = "🎮 Join",
        url2: str = "",
        button3: str = "📢 Socials",
        url3: str = ""
    ):

        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ You need **Manage Server** permission.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"╭・✨ {title}",
            description=(
                f"╰・{description}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"💎 **𝐓𝐡𝐚𝐧𝐤 𝐲𝐨𝐮 𝐟𝐨𝐫 𝐛𝐞𝐢𝐧𝐠 𝐡𝐞𝐫𝐞!**"
            ),
            color=discord.Color.blurple()
        )

        # Author section
        embed.set_author(
            name=f"𝐍𝐨𝐱𝐢𝐚 ♡ • {interaction.guild.name}",
            icon_url=interaction.guild.icon.url
            if interaction.guild.icon else None
        )

        # Thumbnail
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)

        # Big image
        if image:
            embed.set_image(url=image)

        # Fancy fields
        embed.add_field(
            name="╭・🌟 𝐒𝐞𝐫𝐯𝐞𝐫",
            value=f"**{interaction.guild.name}**",
            inline=True
        )

        embed.add_field(
            name="╭・👥 𝐌𝐞𝐦𝐛𝐞𝐫𝐬",
            value=f"**{interaction.guild.member_count:,}**",
            inline=True
        )

        embed.add_field(
            name="╰・🤖 𝐁𝐨𝐭",
            value="**𝐍𝐨𝐱𝐢𝐚 ♡**",
            inline=True
        )

        embed.set_footer(
            text="⚡ 𝐏𝐨𝐰𝐞𝐫𝐞𝐝 𝐛𝐲 𝐍𝐨𝐱𝐢𝐚 ♡ • 𝐌𝐚𝐝𝐞 𝐰𝐢𝐭𝐡 ✨"
        )

        embed.timestamp = discord.utils.utcnow()

        buttons = []

        if url1:
            buttons.append(
                (button1, url1, "🌐")
            )

        if url2:
            buttons.append(
                (button2, url2, "🎮")
            )

        if url3:
            buttons.append(
                (button3, url3, "📢")
            )

        view = FancyButtons(buttons) if buttons else None

        await channel.send(
            embed=embed,
            view=view
        )

        await interaction.response.send_message(
            f"╭・✨ **𝐄𝐦𝐛𝐞𝐝 𝐒𝐞𝐧𝐭!**\n"
            f"╰・📍 {channel.mention}\n"
            f"╰・💎 Premium style enabled.",
            ephemeral=True
        )


# ═══════════════════════════════════════
# 👤 MEMBER JOIN
# ═══════════════════════════════════════

@bot.event
async def on_member_join(member):

    guild_id = str(member.guild.id)
    welcome = config.get(guild_id, {}).get("welcome")

    if not welcome or not welcome.get("enabled"):
        return

    channel = member.guild.get_channel(
        welcome.get("channel")
    )

    if not channel:
        return

    message = welcome["message"].format(
        user=member.mention,
        server=member.guild.name,
        member_count=member.guild.member_count
    )

    embed = discord.Embed(
        title="╭・✨ 𝐖𝐞𝐥𝐜𝐨𝐦𝐞!",
        description=message,
        color=discord.Color.blurple()
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    embed.set_footer(
        text="𝐍𝐨𝐱𝐢𝐚 ♡ • Welcome System"
    )

    embed.timestamp = discord.utils.utcnow()

    await channel.send(embed=embed)


# ═══════════════════════════════════════
# 🤖 BOT READY
# ═══════════════════════════════════════

@bot.event
async def on_ready():

    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands to Discord.")
        print("📋 Commands:", ", ".join(str(cmd) for cmd in synced))
    except Exception as e:
        print(f"❌ Slash command sync failed: {e}")

    print(f"𝐍𝐨𝐱𝐢𝐚 ♡ is online as {bot.user}")


# ═══════════════════════════════════════
# 📋 COMMAND REGISTRATION
# ═══════════════════════════════════════

bot.tree.add_command(WelcomeGroup())
bot.tree.add_command(EmbedGroup())


# ═══════════════════════════════════════
# 🔐 TOKEN
# ═══════════════════════════════════════

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN and os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, "r") as f:
        TOKEN = f.read().strip()

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN environment variable is not set.")

# ───────────── /ping SYSTEM ─────────────

# ───────────── /ping SYSTEM ─────────────
noxia_ping_tasks = {}

@bot.tree.command(name="ping", description="Send a temporary @everyone ping")
async def ping(interaction: discord.Interaction, interval: int = 60):
    if not interaction.user.guild_permissions.mention_everyone:
        await interaction.response.send_message(
            "❌ You need the **Mention Everyone** permission to use this.",
            ephemeral=True
        )
        return

    if interval < 30:
        await interaction.response.send_message(
            "❌ The minimum interval is **30 seconds**.",
            ephemeral=True
        )
        return

    guild_id = interaction.guild.id

    if guild_id in noxia_ping_tasks:
        noxia_ping_tasks[guild_id].cancel()

    await interaction.response.send_message(
        f"✅ @everyone ping started every **{interval}s**. Use `/pingstop` to stop it.",
        ephemeral=True
    )

    async def ping_loop():
        await asyncio.sleep(1)
        while True:
            msg = await interaction.channel.send(
                "@everyone",
                allowed_mentions=discord.AllowedMentions(everyone=True)
            )
            await asyncio.sleep(3)
            try:
                await msg.delete()
            except discord.NotFound:
                pass
            await asyncio.sleep(interval)

    noxia_ping_tasks[guild_id] = asyncio.create_task(ping_loop())


@bot.tree.command(name="pingstop", description="Stop the temporary @everyone ping")
async def pingstop(interaction: discord.Interaction):
    task = noxia_ping_tasks.pop(interaction.guild.id, None)

    if task:
        task.cancel()
        await interaction.response.send_message(
            "🛑 **@everyone ping stopped.**",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "ℹ️ There isn't an active ping loop.",
            ephemeral=True
        )



# ───────────── /video SYSTEM ─────────────
@bot.tree.command(name="video", description="Post a video with a fancy Noxia embed")
async def video(
    interaction: discord.Interaction,
    video: discord.Attachment,
    title: str = "𝐍𝐞𝐰 𝐕𝐢𝐝𝐞𝐨 ✨",
    description: str = "𝐂𝐡𝐞𝐜𝐤 𝐨𝐮𝐭 𝐭𝐡𝐢𝐬 𝐯𝐢𝐝𝐞𝐨! 🎬"
):
    if not video.content_type or not video.content_type.startswith("video/"):
        await interaction.response.send_message(
            "❌ Please upload a **video file**.",
            ephemeral=True
        )
        return

    await interaction.response.defer()

    embed = discord.Embed(
        title=f"╭・🎬 {title}",
        description=(
            f"╰・✨ {description}\n\n"
            f"👤 **𝐏𝐨𝐬𝐭𝐞𝐝 𝐛𝐲:** {interaction.user.mention}\n"
            f"📁 **𝐅𝐢𝐥𝐞:** {video.filename}"
        ),
        timestamp=discord.utils.utcnow()
    )

    embed.set_author(
        name=f"𝐍𝐨𝐱𝐢𝐚 ♡ • {interaction.guild.name}"
    )

    embed.add_field(
        name="🎥 𝐕𝐢𝐝𝐞𝐨",
        value="✨ 𝐄𝐧𝐣𝐨𝐲 𝐭𝐡𝐞 𝐯𝐢𝐝𝐞𝐨!",
        inline=True
    )

    embed.add_field(
        name="👤 𝐂𝐫𝐞𝐚𝐭𝐨𝐫",
        value=interaction.user.mention,
        inline=True
    )

    embed.set_footer(
        text="⚡ 𝐏𝐨𝐰𝐞𝐫𝐞𝐝 𝐛𝐲 𝐍𝐨𝐱𝐢𝐚 ♡ • 𝐌𝐚𝐝𝐞 𝐰𝐢𝐭𝐡 ✨"
    )

    await interaction.followup.send(
        embed=embed,
        file=await video.to_file()
    )


bot.run(TOKEN)
