import random
import asyncio
import time
import discord
from aiohttp import web
import asyncio
from discord import app_commands
from discord.ext import commands
import json
import os

TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN and os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, "r") as f:
        TOKEN = f.read().strip()

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN environment variable is not set.")

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

async def health(request):
    return web.Response(text="Noxia is online!")

WEB_PORT = int(os.getenv("PORT", "10000"))
web_runner = None

async def start_web():
    global web_runner
    app = web.Application()
    app.router.add_get("/", health)
    web_runner = web.AppRunner(app)
    await web_runner.setup()
    site = web.TCPSite(web_runner, "0.0.0.0", WEB_PORT)
    await site.start()
    print(f"🌐 Noxia web server listening on port {WEB_PORT}")

async def main():
    await start_web()
    await bot.start(TOKEN)


# ==================== AUTOMATIC EVENT SYSTEM ====================

EVENT_NAMES = [
    "⚡ Lightning Rush",
    "🎮 Mystery Game Night",
    "🏆 Champion Challenge",
    "🎲 Random Challenge",
    "💎 Diamond Hunt",
    "🔥 Ultimate Showdown",
    "🌟 Star Event",
    "🚀 Speed Challenge"
]

EVENT_REWARDS = [
    "💎 500 Server Coins",
    "🏆 Exclusive Winner Role",
    "⭐ VIP Role for 7 Days",
    "🎁 Mystery Prize",
    "⚡ Special Event Badge",
    "💰 1,000 Server Coins"
]

class EventJoinButton(discord.ui.Button):
    def __init__(self, event_data):
        super().__init__(
            label="✨ JOIN EVENT",
            emoji="🎉",
            style=discord.ButtonStyle.success,
            custom_id=f"event_join_{event_data['id']}"
        )
        self.event_data = event_data

    async def callback(self, interaction: discord.Interaction):
        data = self.event_data

        if time.time() >= data["ends"]:
            await interaction.response.send_message(
                "⏰ This event has already ended!",
                ephemeral=True
            )
            return

        if interaction.user.id not in data["players"]:
            data["players"].append(interaction.user.id)
            await interaction.response.send_message(
                f"🎉 **You're in!**\n\n"
                f"✨ Event: **{data['name']}**\n"
                f"🎁 Reward: **{data['reward']}**\n"
                f"🔗 Invite: {data['invite']}",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "⚡ You're already entered!",
                ephemeral=True
            )

class EventView(discord.ui.View):
    def __init__(self, data):
        super().__init__(timeout=None)
        self.data = data
        self.join_button = EventJoinButton(data)
        self.add_item(self.join_button)

@bot.tree.command(name="event", description="🎉 Start a random automatic event")
async def event(interaction: discord.Interaction):

    channel = interaction.channel

    try:
        invite = await channel.create_invite(
            max_age=180,
            max_uses=0,
            unique=True,
            reason="𝐍𝐨𝐱𝐢𝐚 ♡ automatic event"
        )
    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ I need **Create Invite** permission in this channel.",
            ephemeral=True
        )
        return
    except Exception as e:
        await interaction.response.send_message(
            f"❌ I couldn't create the event invite.\n`{e}`",
            ephemeral=True
        )
        return

    duration = random.randint(45, 120)
    name = random.choice(EVENT_NAMES)
    reward = random.choice(EVENT_REWARDS)

    data = {
        "id": random.randint(100000, 999999999),
        "name": name,
        "reward": reward,
        "invite": str(invite),
        "ends": time.time() + duration,
        "players": []
    }

    minutes = duration // 60
    seconds = duration % 60
    timer_text = f"{minutes}m {seconds}s" if minutes else f"{seconds}s"

    embed = discord.Embed(
        title="╭━━━ ✨ 𝐍𝐎𝐗𝐈𝐀 𝐄𝐕𝐄𝐍𝐓 ✨ ━━━╮",
        description=(
            f"🎉 **A RANDOM EVENT HAS APPEARED!**\n\n"
            f"🎲 **Event:** {name}\n"
            f"🎁 **Random Reward:** {reward}\n"
            f"⏳ **Time:** `{timer_text}`\n"
            f"👥 **Players:** `0`\n\n"
            f"🔗 **Event Invite:**\n{invite}\n\n"
            f"⚡ Click **✨ JOIN EVENT** to enter!\n"
            f"🏆 One lucky participant will be selected when the timer ends!"
        ),
        color=discord.Color.blurple()
    )

    embed.set_footer(text="𝐍𝐨𝐱𝐢𝐚 ♡ • Automatic Events")
    embed.timestamp = discord.utils.utcnow()

    view = EventView(data)

    await interaction.response.send_message(
        embed=embed,
        view=view
    )

    message = await interaction.original_response()

    # Countdown / live player count
    while time.time() < data["ends"]:
        await asyncio.sleep(5)

        remaining = max(0, int(data["ends"] - time.time()))
        mins = remaining // 60
        secs = remaining % 60

        embed.description = (
            f"🎉 **A RANDOM EVENT HAS APPEARED!**\n\n"
            f"🎲 **Event:** {name}\n"
            f"🎁 **Random Reward:** {reward}\n"
            f"⏳ **Time Left:** `{mins}m {secs}s`\n"
            f"👥 **Players:** `{len(data['players'])}`\n\n"
            f"🔗 **Event Invite:**\n{invite}\n\n"
            f"⚡ Click **✨ JOIN EVENT** to enter!"
        )

        try:
            await message.edit(embed=embed, view=view)
        except discord.NotFound:
            return
        except discord.HTTPException:
            pass

    # End event
    view.join_button.disabled = True
    view.join_button.label = "🏁 EVENT ENDED"

    if data["players"]:
        winner_id = random.choice(data["players"])
        winner = interaction.guild.get_member(winner_id)

        if winner:
            result = (
                f"🏆 **WINNER:** {winner.mention}\n"
                f"🎁 **REWARD:** {reward}\n\n"
                f"🎉 Congratulations!"
            )
        else:
            result = (
                f"🏆 **Winner ID:** `{winner_id}`\n"
                f"🎁 **Reward:** {reward}"
            )
    else:
        result = (
            "😢 **No one joined the event.**\n"
            "There was no winner this time!"
        )

    final_embed = discord.Embed(
        title="╭━━━ 🏁 𝐄𝐕𝐄𝐍𝐓 𝐄𝐍𝐃𝐄𝐃 🏁 ━━━╮",
        description=(
            f"🎲 **Event:** {name}\n"
            f"🎁 **Reward:** {reward}\n"
            f"👥 **Participants:** {len(data['players'])}\n\n"
            f"{result}"
        ),
        color=discord.Color.gold()
    )

    final_embed.set_footer(text="𝐍𝐨𝐱𝐢𝐚 ♡ • Event Complete")
    final_embed.timestamp = discord.utils.utcnow()

    try:
        await message.edit(embed=final_embed, view=view)
    except discord.HTTPException:
        pass


asyncio.run(main())


# ──────────────── EXTRA COMMANDS ────────────────

ping_task = None

@bot.tree.command(name="ping", description="📢 Start a controlled @everyone ping timer")
@app_commands.describe(interval="Seconds between pings (minimum 30)")
async def ping(interaction: discord.Interaction, interval: int):
    global ping_task

    if interval < 30:
        await interaction.response.send_message(
            "❌ The minimum interval is **30 seconds**.",
            ephemeral=True
        )
        return

    if ping_task and not ping_task.done():
        await interaction.response.send_message(
            "⚠️ A ping timer is already running.",
            ephemeral=True
        )
        return

    if not interaction.channel.permissions_for(interaction.guild.me).mention_everyone:
        await interaction.response.send_message(
            "❌ I need the **Mention @everyone, @here, and All Roles** permission.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"⚡ **𝐏𝐢𝐧𝐠 𝐓𝐢𝐦𝐞𝐫 𝐒𝐭𝐚𝐫𝐭𝐞𝐝**\n"
        f"📢 @everyone every **{interval} seconds**.\n"
        f"🛑 Use `/pingstop` to stop it."
    )

    async def ping_loop():
        try:
            while True:
                await asyncio.sleep(interval)
                msg = await interaction.channel.send(
                    f"⚡ **𝐍𝐨𝐱𝐢𝐚 𝐏𝐢𝐧𝐠**\n@everyone"
                )
                await asyncio.sleep(3)
                try:
                    await msg.delete()
                except discord.NotFound:
                    pass
        except asyncio.CancelledError:
            pass

    ping_task = asyncio.create_task(ping_loop())


@bot.tree.command(name="pingstop", description="🛑 Stop the active ping timer")
async def pingstop(interaction: discord.Interaction):
    global ping_task

    if ping_task and not ping_task.done():
        ping_task.cancel()
        ping_task = None
        await interaction.response.send_message(
            "🛑 **𝐏𝐢𝐧𝐠 𝐓𝐢𝐦𝐞𝐫 𝐒𝐭𝐨𝐩𝐩𝐞𝐝**"
        )
    else:
        await interaction.response.send_message(
            "ℹ️ There is no active ping timer.",
            ephemeral=True
        )


@bot.tree.command(name="video", description="🎬 Post a video with a fancy embed")
@app_commands.describe(
    video="Upload the video",
    title="Embed title",
    description="Embed description"
)
async def video(
    interaction: discord.Interaction,
    video: discord.Attachment,
    title: str = "🎬 𝐍𝐨𝐱𝐢𝐚 𝐕𝐢𝐝𝐞𝐨",
    description: str = "✨ Check out this video!"
):
    if not video.content_type or not video.content_type.startswith("video/"):
        await interaction.response.send_message(
            "❌ Please upload a valid video file.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title=f"⚡ {title}",
        description=description,
        color=discord.Color.blurple()
    )

    embed.set_author(
        name="𝐍𝐨𝐱𝐢𝐚 ♡",
        icon_url=bot.user.display_avatar.url if bot.user else None
    )
    embed.set_footer(text="✨ Powered by 𝐍𝐨𝐱𝐢𝐚 ♡")
    embed.timestamp = discord.utils.utcnow()

    await interaction.response.send_message(
        embed=embed,
        file=await video.to_file()
    )
