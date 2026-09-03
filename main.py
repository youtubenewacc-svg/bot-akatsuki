import asyncio
import datetime
import os
import re
import time
import discord
from discord import app_commands
from discord.ext import commands

# ---------------------------------------------------------
# 1. إعداد الـ Intents
# ---------------------------------------------------------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="+", intents=intents)

# ---------------------------------------------------------
# الإعدادات العامة والأيدي (IDs)
# ---------------------------------------------------------
BOT_ADMIN_ID = 1241496820455313533
DEVELOPER_NAME = "JrOmar"

TAX_CHANNEL_ID = 1534698357400932383
FEEDBACK_CHANNEL_ID = 1534698367983292558
ACCEPTED_ROLE_ID = 1536068615940472992
PIC_ROLE_ID = 1534698182162911446

VOICE_CHANNEL_ID = 1537441135935627386
CUSTOM_EMOJI_REACTION = "<:Akatsuki:1534740400793976862>"

# ---------------------------------------------------------
# نظام الـ AFK (تخزين بيانات المستخدمين)
# ---------------------------------------------------------
afk_users = {}

TICKET_SHOP_CHANNELS = [
    1534698295711236106,
    1534698299066421399,
]

OBFUSCATE_CHANNELS = [
    1534698295711236106,
    1534698299066421399,
]

TICKET_SHOP_URL = (
    "https://discord.com/channels/1518323757494697994/1534698361301504020"
)

AUTO_LINE_CHANNELS = [
    1534698295711236106,
    1534698299066421399,
    1534698302401151166,
    1534698309611163658,
    1534698312895168582,
    1534698323057971210,
    1534698326337781911,
    1534698329852743861,
    1534698333556183182,
    1534698337029193908,
]

LINE_IMAGE_URL = "https://imgur.com/a/obsZpn3"

COME_ROLES = [1534723709867393146]
LINE_ROLES = [1534723678149935296]
BC_ROLES = [1534723709867393146]
SAY_ROLES = [1534723709867393146]

BAD_WORDS = [
    "zaml", "w9", "wl9", "9hba", "wlld l9hba", "lay3eltbonmo", "mok", "b9", "bntl9hba", "zbi",
    "شرموطه", "نصاب", "كسمك", "زامل", "قحبة", "ولد القحبة", "طبون", "زب", "زبي"
]

REPLACEMENT_RULES = {
    "نيترو": "نيتر9",
    "متوفر": "مت9فر",
    "سعر": "س3ر",
    "nitro": "n!tr0",
    "compte": "c0mpt€",
    "acc": "@çç",
    "بوستات": "ب9ستات",
    "بوست": "ب9ست",
    "كردت": "كردt",
    "طرق": "طر/ق",
    "الدفع": "الدف/ع",
    "مطلوب": "مطل9ب",
    "حسابات": "7سابات",
    "حساب": "7ساب",
    "قوقل": "ق9قل",
    "كريبتو": "ك/يبتو",
    "تفعيل": "تف3يل",
    "فيزا": "في/زا",
}

def obfuscate_text(text: str) -> str:
    result = text
    for word, replacement in REPLACEMENT_RULES.items():
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        result = pattern.sub(replacement, result)
    return result

def check_roles(allowed_roles):
    async def predicate(interaction: discord.Interaction):
        if interaction.user.id == BOT_ADMIN_ID:
            return True
        if interaction.user.guild_permissions.administrator:
            return True

        try:
            member = await interaction.guild.fetch_member(interaction.user.id)
        except Exception:
            member = interaction.user

        user_role_ids = [role.id for role in member.roles]

        if any(role_id in allowed_roles for role_id in user_role_ids):
            return True

        await interaction.response.send_message(
            "⛔ **عذراً!** ليس لديك الرتبة المخصصة لاستخدام هذا الأمر.",
            ephemeral=True,
        )
        return False

    return discord.app_commands.check(predicate)

# ---------------------------------------------------------
# 2. UI Components (Views, Modals)
# ---------------------------------------------------------
class CopyObfuscatedView(discord.ui.View):
    def __init__(self, obfuscated_text: str):
        super().__init__(timeout=120)
        self.obfuscated_text = obfuscated_text

    @discord.ui.button(
        label="📋 نسخ النص المشفر",
        style=discord.ButtonStyle.success,
        custom_id="copy_obfuscated_code_btn",
    )
    async def copy_button_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message(
            f"📋 **انسخ النص من الكود أسفله:**\n```text\n{self.obfuscated_text}\n```",
            ephemeral=True,
        )

class ObfuscateModal(discord.ui.Modal, title="🔒 تشفير النص تلقائياً"):
    user_input = discord.ui.TextInput(
        label="أدخل النص المراد تشفيره:",
        style=discord.TextStyle.paragraph,
        placeholder="مثال: متوفر حسابات نيترو للبيع، طرق الدفع فيزا أو كريبتو...",
        required=True,
        max_length=2000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        original_text = self.user_input.value
        processed_text = obfuscate_text(original_text)

        embed = discord.Embed(
            title="✨ تم تشفير النص بنجاح!",
            color=discord.Color.green(),
        )
        embed.add_field(
            name="📝 النص بعد التشفير:",
            value=f"{processed_text}",
            inline=False,
        )
        embed.set_footer(text="يمكنك الضغط على الزر أسفله لنسخ النص بسهولة.")

        view = CopyObfuscatedView(processed_text)
        await interaction.response.send_message(
            embed=embed, view=view, ephemeral=True
        )

class ObfuscateMainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🔒 تشفير النص",
        style=discord.ButtonStyle.primary,
        custom_id="start_obfuscate_modal_btn",
    )
    async def start_obfuscate(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_modal(ObfuscateModal())

TEXT_TO_COPY = """**المنتج :




الس3ر :




للشراء افتح تذكرة الطلب 



ل : <@&1534698177628868629>**"""

class TicketShopView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        copy_btn = discord.ui.Button(
            label="نسخ",
            style=discord.ButtonStyle.blurple,
            custom_id="copy_form_btn_persistent",
        )
        copy_btn.callback = self.copy_callback
        self.add_item(copy_btn)

        shop_btn = discord.ui.Button(
            label="تكت طلب",
            style=discord.ButtonStyle.link,
            url=TICKET_SHOP_URL,
        )
        self.add_item(shop_btn)

    async def copy_callback(self, interaction: discord.Interaction):
        copy_message = f"📋 **انسخ النص أسفله بضغطة واحدة:**\n\n```text\n{TEXT_TO_COPY}\n```"
        await interaction.response.send_message(
            copy_message, ephemeral=True
        )

# ---------------------------------------------------------
# Setup Hook & Events
# ---------------------------------------------------------
async def setup_hook():
    bot.add_view(TicketShopView())
    bot.add_view(ObfuscateMainView())

bot.setup_hook = setup_hook

@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        print("Synced global slash commands successfully!")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

    print("==========================================")
    print(f"System Bot is online as: {bot.user.name}")
    print(f"Developer: {DEVELOPER_NAME}")
    print("==========================================")

    try:
        channel = bot.get_channel(VOICE_CHANNEL_ID)
        if not channel:
            channel = await bot.fetch_channel(VOICE_CHANNEL_ID)

        if isinstance(channel, discord.VoiceChannel):
            if not bot.voice_clients:
                await channel.connect(reconnect=True, self_deaf=True)
                print(f"✅ SUCCESSFULLY joined voice channel: {channel.name}")
    except Exception as e:
        print(f"❌ CRITICAL VOICE ERROR: {e}")

async def remove_user_roles(guild: discord.Guild, member: discord.Member):
    roles_to_remove = [role for role in member.roles if role != guild.default_role]
    if not roles_to_remove:
        return False, "⚠️ هذا العضو لا يملك أي رولات لإزالتها."

    try:
        await member.remove_roles(*roles_to_remove)
        return True, "<:GreenCheckMark:1534743839762546849>لقد تم ازالة رولات هذا العضو بنجاح"
    except discord.Forbidden:
        return False, "❌ البوت لا يملك الصلاحيات الكافية لإزالة رولات هذا العضو."
    except Exception as e:
        return False, f"❌ حدث خطأ أثناء إزالة الرولات: `{e}`"

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    content_raw = message.content.strip()
    content_clean = content_raw.lower()

    if content_clean == ".afk" or content_clean.startswith(".afk "):
        reason_text = content_raw[4:].strip()
        reason = reason_text if reason_text else "لا يوجد سبب محدد / No reason provided"
        
        afk_users[message.author.id] = {
            "reason": reason,
            "time": time.time(),
            "mentions": []
        }

        embed = discord.Embed(
            author=discord.EmbedAuthor(name=message.author.display_name, icon_url=message.author.display_avatar.url),
            description="**AFK Set! You are now AFK in all servers.**\nلقد دخلت الآن في وضع الـ AFK بنجاح.",
            color=discord.Color.from_rgb(47, 49, 54)
        )
        if reason_text:
            embed.set_footer(text=f"Reason: {reason}")

        await message.channel.send(embed=embed)
        return

    if message.author.id in afk_users:
        user_afk_data = afk_users.pop(message.author.id)
        duration_seconds = int(time.time() - user_afk_data["time"])
        
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_str = ""
        if hours > 0:
            duration_str += f"{hours}h "
        if minutes > 0 or hours > 0:
            duration_str += f"{minutes}m "
        duration_str += f"{seconds}s"

        mentions_list = user_afk_data["mentions"]
        
        embed = discord.Embed(
            title="👋 مرحباً بعودتك! / Welcome Back!",
            description=f"لقد تم إلغاء وضع الـ AFK تلقائياً.\nYou are no longer AFK.\n\n⏱️ **المدة / Duration:** `{duration_str}`\n💬 **عدد الإشارات / Mentions:** `{len(mentions_list)}`",
            color=discord.Color.green()
        )

        if mentions_list:
            mentions_text = ""
            for idx, m in enumerate(mentions_list[:10], 1):
                mentions_text += f"**{idx}.** {m['author']} ({m['time']}): [Jump to message]({m['jump_url']})\n> {m['content']}\n\n"
            
            if len(mentions_list) > 10:
                mentions_text += f"*...and {len(mentions_list) - 10} more mentions.*"
            
            embed.add_field(name="📩 الأشخاص الذين قاموا بالإشارة إليك:", value=mentions_text, inline=False)

        await message.channel.send(embed=embed)

    if message.mentions:
        for mentioned_user in message.mentions:
            if mentioned_user.id in afk_users and mentioned_user.id != message.author.id:
                user_data = afk_users[mentioned_user.id]
                
                now_str = (discord.utils.utcnow() + datetime.timedelta(hours=1)).strftime("%H:%M")
                
                user_data["mentions"].append({
                    "author": message.author.display_name,
                    "content": message.content[:100],
                    "time": now_str,
                    "jump_url": message.jump_url
                })

                embed_room = discord.Embed(
                    description=f"**{mentioned_user.display_name}** is currently AFK.",
                    color=discord.Color.from_rgb(47, 49, 54)
                )
                if user_data["reason"] != "لا يوجد سبب محدد / No reason provided":
                    embed_room.set_footer(text=f"Reason: {user_data['reason']}")

                await message.channel.send(embed=embed_room)

                try:
                    dm_embed = discord.Embed(
                        title="🔔 إشعار إشارة (Tag Notification)",
                        description=f"قام **{message.author.display_name}** بالإشارة إليك في روم {message.channel.mention} بينما كنت في وضع **AFK**.",
                        color=discord.Color.gold()
                    )
                    dm_embed.add_field(name="محتوى الرسالة:", value=f"> {message.content[:200]}", inline=False)
                    dm_embed.add_field(name="رابط الرسالة:", value=f"[انتقل للرسالة]({message.jump_url})", inline=False)
                    dm_embed.set_footer(text=f"الوقت: {now_str}")
                    
                    await mentioned_user.send(embed=dm_embed)
                except discord.Forbidden:
                    pass
                
                break

    if content_clean in ["السلام عليكم", "سلام عليكم", "سلام عليكم ورحمة الله", "السلام عليكم ورحمة الله وبركاته"]:
        try:
            await message.channel.send("وعليكم السلام منور/ه<:vxy:1534699071263084645>")
        except Exception as e:
            print(f"Error sending salam response: {e}")

    if content_clean in ["link", "link bio", "bio", "رابط"]:
        try:
            await message.channel.send("https://discord.gg/aEyTkGuvE9")
            return
        except Exception as e:
            print(f"Error sending link: {e}")

    if message.channel.id == FEEDBACK_CHANNEL_ID:
        try:
            await message.delete()
        except Exception:
            pass

        contains_bad_word = any(bad_word in content_clean for bad_word in BAD_WORDS)

        if contains_bad_word:
            try:
                await message.author.send("⚠️ **عذراً، يحتوي تقييمك على كلمات محظورة وتم إلغاؤه!**")
            except Exception:
                pass
            return

        author = message.author
        raw_text = message.content.strip()

        embed = discord.Embed(
            description=f"**{raw_text}** {CUSTOM_EMOJI_REACTION}",
            color=discord.Color.from_rgb(47, 49, 54)
        )

        embed.set_author(
            name=author.display_name,
            icon_url=author.display_avatar.url
        )

        if message.guild and message.guild.icon:
            embed.set_thumbnail(url=message.guild.icon.url)

        now_time = discord.utils.utcnow() + datetime.timedelta(hours=1)
        now_str = now_time.strftime("%d/%m/%Y %H:%M")
        
        server_name = message.guild.name if message.guild else "Server"
        embed.set_footer(
            text=f"#~ {server_name} • {now_str}",
            icon_url=bot.user.display_avatar.url
        )

        try:
            sent_msg = await message.channel.send(embed=embed)
            await sent_msg.add_reaction(CUSTOM_EMOJI_REACTION)
        except Exception as e:
            print(f"Error sending feedback: {e}")
        return

    if content_clean == "+pic":
        pic_role = message.guild.get_role(PIC_ROLE_ID)
        if not pic_role:
            await message.channel.send("❌ لم يتم العثور على رتبة الصور في السيرفر.")
            return

        try:
            await message.author.add_roles(pic_role)
            await message.channel.send(
                "لقد تم اعطائك رول الصور بنجاح<:GreenCheckMark:1534743839762546849>"
            )
        except discord.Forbidden:
            await message.channel.send("❌ البوت لا يملك الصلاحيات الكافية لإعطائك هذه الرتبة.")
        except Exception as e:
            await message.channel.send(f"❌ حدث خطأ أثناء إعطاء الرتبة: `{e}`")
        return

    if content_clean.startswith("rar"):
        if not message.author.guild_permissions.manage_roles:
            await message.channel.send("❌ ليس لديك صلاحية `Manage Roles` لاستخدام هذا الأمر.")
            return

        target_member = None
        if message.mentions:
            target_member = message.mentions[0]
        else:
            args = message.content.split()
            if len(args) > 1:
                clean_id = re.sub(r"[<@!>]", "", args[1])
                if clean_id.isdigit():
                    try:
                        target_member = await message.guild.fetch_member(int(clean_id))
                    except discord.NotFound:
                        target_member = None

        if not target_member:
            await message.channel.send("❌ يرجى منشن العضو أو وضع الـ ID الخاص به (مثال: `rar @user`).")
            return

        success, response_msg = await remove_user_roles(message.guild, target_member)
        await message.channel.send(response_msg)
        return

    if "مقبول" in content_clean and message.mentions and message.guild:
        role = message.guild.get_role(ACCEPTED_ROLE_ID)
        if role:
            for member in message.mentions:
                try:
                    await member.add_roles(role)
                    await message.channel.send(
                        f"{member.mention} لقد تم قبولك <:GreenCheckMark:1534743839762546849>"
                    )
                except Exception as e:
                    print(f"Failed to give role to {member.display_name}: {e}")

    if content_clean in ["line", "خط"]:
        try:
            await message.delete()
        except Exception:
            pass
        try:
            await message.channel.send(LINE_IMAGE_URL)
        except Exception as e:
            print(f"Error sending line image: {e}")
        return

    if message.channel.id == TAX_CHANNEL_ID:
        if re.match(r"^\d+(\.\d+)?[kmb]?$", content_clean):
            try:
                clean_amount = (
                    content_clean.replace("k", "000")
                    .replace("m", "000000")
                    .replace("b", "000000000")
                    .replace(",", "")
                )
                number = int(float(clean_amount))

                if number > 0:
                    with_tax = int(number / 0.95) + 1
                    tax_only = with_tax - number

                    embed = discord.Embed(
                        title="💳 حاسبة ضريبة تلقائية",
                        color=discord.Color.green(),
                    )
                    embed.add_field(
                        name="💵 المبلغ المطلوب وصوله:",
                        value=f"`{number:,}`",
                        inline=False,
                    )
                    embed.add_field(
                        name="💰 المبلغ الذي يجب تحويله (مع الضريبة):",
                        value=f"`{with_tax:,}`",
                        inline=False,
                    )
                    embed.add_field(
                        name="📉 قيمة الضريبة (5%):",
                        value=f"`{tax_only:,}`",
                        inline=False,
                    )
                    embed.set_footer(
                        text=f"Requested by {message.author.display_name}"
                    )

                    try:
                        await message.delete()
                    except Exception:
                        pass

                    await message.channel.send(embed=embed)
            except ValueError:
                pass

    if message.channel.id in AUTO_LINE_CHANNELS:
        try:
            await message.channel.send(LINE_IMAGE_URL)
        except Exception as e:
            print(f"Error sending auto line: {e}")

    await bot.process_commands(message)

# ---------------------------------------------------------
# Slash Commands
# ---------------------------------------------------------
@bot.tree.command(name="createtemporaryroom", description="إنشاء روم مؤقتة تنحذف تلقائياً بعد مدة محددة")
@app_commands.describe(
    name="اسم الروم",
    time_value="مقدار الوقت (مثال: 10 أو 2)",
    time_unit="وحدة الوقت (دقائق، ساعات، أيام)",
    category="الكاتيجوري المراد إنشاء الروم فيها",
    allow_everyone="هل يسمح للجميع بالكتابة؟ (True للجميع / False للأدمن فقط)",
    topic="وصف اختياري للروم"
)
@app_commands.choices(time_unit=[
    app_commands.Choice(name="Minutes / دقائق", value="minutes"),
    app_commands.Choice(name="Hours / ساعات", value="hours"),
    app_commands.Choice(name="Days / أيام", value="days")
])
@app_commands.checks.has_permissions(manage_channels=True)
async def create_temporary_room(
    interaction: discord.Interaction,
    name: str,
    time_value: int,
    time_unit: app_commands.Choice[str],
    category: discord.CategoryChannel,
    allow_everyone: bool,
    topic: str = None
):
    if time_value <= 0:
        await interaction.response.send_message("❌ يرجى تحديد قيمة وقت أكبر من 0.", ephemeral=True)
        return

    # حساب الوقت بالثواني بناءً على الوحدة المختارة
    if time_unit.value == "minutes":
        total_seconds = time_value * 60
        unit_label = "دقيقة"
    elif time_unit.value == "hours":
        total_seconds = time_value * 3600
        unit_label = "ساعة"
    elif time_unit.value == "days":
        total_seconds = time_value * 86400
        unit_label = "يوم"

    overwrites = {
        interaction.guild.default_role: discord.PermissionOverwrite(
            read_messages=True,
            send_messages=allow_everyone
        )
    }

    try:
        temp_channel = await interaction.guild.create_text_channel(
            name=name,
            category=category,
            overwrites=overwrites,
            topic=topic
        )

        permissions_status = "الجميع يستطيع الكتابة 💬" if allow_everyone else "الأدمن فقط يستطيع الكتابة 🔒"
        
        embed = discord.Embed(
            title="⏱️ تم إنشاء الروم المؤقتة بنجاح!",
            description=f"**الروم:** {temp_channel.mention}\n**المدة:** `{time_value}` {unit_label}\n**صلاحية الكتابة:** {permissions_status}",
            color=discord.Color.green()
        )
        if topic:
            embed.add_field(name="الوصف:", value=topic, inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

        welcome_embed = discord.Embed(
            title="⚠️ روم مؤقتة (Temporary Room)",
            description=f"هذه الروم مؤقتة وسوف تُحذف تلقائياً بعد **{time_value} {unit_label}**.\n\n**صلاحية الكتابة:** {permissions_status}",
            color=discord.Color.gold()
        )
        welcome_embed.set_footer(text=f"تم إنشاؤها بواسطة {interaction.user.display_name}")
        await temp_channel.send(embed=welcome_embed)

        async def delete_channel_after_delay():
            await asyncio.sleep(total_seconds)
            try:
                await temp_channel.delete(reason="انتهت مدة الروم المؤقتة")
            except Exception as e:
                print(f"Error deleting temporary room: {e}")

        asyncio.create_task(delete_channel_after_delay())

    except discord.Forbidden:
        await interaction.response.send_message("❌ البوت لا يملك صلاحية إنشاء القنوات في هذه الكاتيجوري.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ حدث خطأ أثناء إنشاء الروم: `{e}`", ephemeral=True)

@bot.tree.command(name="clear_roles", description="إزالة جميع الرولات من عضو معين")
@discord.app_commands.describe(user_input="اختر العضو أو ادخل الـ ID الخاص به")
@discord.app_commands.checks.has_permissions(manage_roles=True)
async def clear_roles(interaction: discord.Interaction, user_input: str):
    await interaction.response.defer()
    
    member = None
    clean_id = re.sub(r"[<@!>]", "", user_input)
    if clean_id.isdigit():
        try:
            member = await interaction.guild.fetch_member(int(clean_id))
        except discord.NotFound:
            member = None

    if not member:
        await interaction.followup.send("❌ لم يتم العثور على هذا العضو في السيرفر.", ephemeral=True)
        return

    success, response_msg = await remove_user_roles(interaction.guild, member)
    await interaction.followup.send(response_msg)

@bot.tree.command(name="feedbacks", description="إرسال تقييم أو رأي")
@discord.app_commands.describe(text="اكتب رأيك أو التقييم الخاص بك")
async def feedbacks_command(interaction: discord.Interaction, text: str):
    text_lower = text.lower()
    contains_bad_word = any(bad_word in text_lower for bad_word in BAD_WORDS)

    if contains_bad_word:
        await interaction.response.send_message(
            "⚠️ **عذراً، يحتوي تقييمك على كلمات غير لائقة وتم إلغاؤه!**",
            ephemeral=True
        )
        return

    author = interaction.user

    embed = discord.Embed(
        description=f"**{text}** {CUSTOM_EMOJI_REACTION}",
        color=discord.Color.from_rgb(47, 49, 54)
    )

    embed.set_author(
        name=author.display_name,
        icon_url=author.display_avatar.url
    )

    if interaction.guild and interaction.guild.icon:
        embed.set_thumbnail(url=interaction.guild.icon.url)

    now_time = discord.utils.utcnow() + datetime.timedelta(hours=1)
    now_str = now_time.strftime("%d/%m/%Y %H:%M")

    server_name = interaction.guild.name if interaction.guild else "Server"
    embed.set_footer(
        text=f"#~ {server_name} • {now_str}",
        icon_url=bot.user.display_avatar.url
    )

    sent_msg = await interaction.channel.send(embed=embed)
    await sent_msg.add_reaction(CUSTOM_EMOJI_REACTION)

    await interaction.response.send_message("✅ تم إرسال تقييمك بنجاح!", ephemeral=True)

@bot.tree.command(name="obfuscate", description="إرسال لوحة تشفير الكلمات لمنع الحظر")
async def send_obfuscate_panel(interaction: discord.Interaction):
    if (
        interaction.channel.id not in OBFUSCATE_CHANNELS
        and not interaction.user.guild_permissions.administrator
    ):
        await interaction.response.send_message(
            "❌ هذا الأمر غير مسموح به في هذه الروم.", ephemeral=True
        )
        return

    embed = discord.Embed(
        title="🔒 أداة تشفير النصوص والكلمات",
        description=(
            "اضغط على الزر أسفله لكتابة إعلانك أو نصك، وسيقوم البوت بتشفير الكلمات "
            "الحساسة تلقائياً (مثل: ניתר9, 7ساب, تف3يل... إلخ) لتفادي الفلترة."
        ),
        color=discord.Color.blurple(),
    )
    if interaction.guild.icon:
        embed.set_thumbnail(url=interaction.guild.icon.url)

    embed.set_footer(text=f"Sent by {interaction.user.display_name}")

    view = ObfuscateMainView()
    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message(
        "✅ تم إرسال لوحة التشفير بنجاح!", ephemeral=True
    )

@bot.tree.command(name="ticket_shop", description="إرسال إمبد الفورمولا للتكت والمنتجات")
async def ticket_shop_command(interaction: discord.Interaction):
    if (
        interaction.channel.id not in TICKET_SHOP_CHANNELS
        and not interaction.user.guild_permissions.administrator
    ):
        await interaction.response.send_message(
            "❌ هذا الأمر غير مسموح به في هذه الروم.", ephemeral=True
        )
        return

    embed = discord.Embed(
        title="Akatsuki S",
        description=(
            "**المنتج :**\n\n"
            "**الس3ر :**\n\n"
            "**للشراء افتح تذكرة الطلب :**\n\n"
            "**ل :** <@&1534698177628868629>"
        ),
        color=discord.Color.gold(),
    )

    if interaction.guild.icon:
        embed.set_thumbnail(url=interaction.guild.icon.url)

    embed.set_footer(
        text=f"Akatsuki S · Formulaire | Sent by {interaction.user.display_name}"
    )

    view = TicketShopView()
    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message("✅ تم إرسال Formulaire بنجاح!", ephemeral=True)

@bot.tree.command(name="tax", description="حساب ضريبة التحويل ProBot 5%")
@discord.app_commands.describe(amount="المبلغ المراد حسابه (مثال: 100k أو 50000)")
async def calculate_tax(interaction: discord.Interaction, amount: str):
    if interaction.channel.id != TAX_CHANNEL_ID:
        await interaction.response.send_message(
            f"❌ عذراً، أمر الـ Tax مسموح به فقط في روم <#{TAX_CHANNEL_ID}>!",
            ephemeral=True,
        )
        return

    try:
        clean_amount = (
            amount.lower()
            .replace("k", "000")
            .replace("m", "000000")
            .replace(",", "")
        )
        number = int(clean_amount)

        if number <= 0:
            await interaction.response.send_message(
                "❌ يرجى إدخال مبلغ صحيح أكبر من 0.", ephemeral=True
            )
            return

        with_tax = int(number / 0.95) + 1
        tax_only = with_tax - number

        embed = discord.Embed(
            title="💳 حاسبة ضريبة", color=discord.Color.green()
        )
        embed.add_field(
            name="💵 المبلغ المطلوب وصوله:",
            value=f"`{number:,}`",
            inline=False,
        )
        embed.add_field(
            name="💰 المبلغ الذي يجب تحويله (مع الضريبة):",
            value=f"`{with_tax:,}`",
            inline=False,
        )
        embed.add_field(
            name="📉 قيمة الضريبة (5%):", value=f"`{tax_only:,}`", inline=False
        )
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")

        await interaction.response.send_message(embed=embed)

    except ValueError:
        await interaction.response.send_message(
            "❌ صيغة المبلغ غير صحيحة! مثال: `50k` أو `10000`.", ephemeral=True
        )

@bot.tree.command(name="come", description="إرسال طلب حضور (استدعاء) لعضو في الخاص")
@discord.app_commands.describe(user_id="أيدي العضو المراد استدعاؤه")
@check_roles(COME_ROLES)
async def come_user(interaction: discord.Interaction, user_id: str):
    try:
        uid = int(user_id)
        member = await interaction.guild.fetch_member(uid)
        if not member:
            await interaction.response.send_message(
                "❌ هذا العضو غير موجود في هذا السيرفر.", ephemeral=True
            )
            return

        embed = discord.Embed(
            title="📩 استدعاء / Summon Request",
            description=f"سلام **{member.display_name}**، العضو **{interaction.user.mention}** يطلب حضورك الآن في سيرفر **{interaction.guild.name}**!",
            color=discord.Color.gold(),
        )

        if interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)

        embed.set_footer(text=f"Server: {interaction.guild.name}")

        try:
            await member.send(embed=embed)
            await interaction.response.send_message(
                f"✅ تم إرسال طلب الحضور إلى {member.mention} في الخاص!"
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                f"❌ ما قدرتش نصيفط لـ {member.mention} فـ الخاص حيت ساد الـ DM.",
                ephemeral=True,
            )

    except ValueError:
        await interaction.response.send_message(
            "❌ يرجى إدخال أيدي (ID) صحيح للعضو.", ephemeral=True
        )
    except discord.NotFound:
        await interaction.response.send_message(
            "❌ لم يتم العثور على هذا العضو فـ السيرفر.", ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(
            f"❌ حدث خطأ: `{e}`", ephemeral=True
        )

@bot.tree.command(name="line", description="إرسال خط فاصل بصورة في الشات")
@discord.app_commands.describe(image_url="رابط الصورة المراد إرسالها (اختياري)")
@check_roles(LINE_ROLES)
async def send_line(interaction: discord.Interaction, image_url: str = None):
    try:
        target_url = image_url if image_url else LINE_IMAGE_URL
        await interaction.response.send_message(target_url)
    except Exception as e:
        await interaction.response.send_message(
            f"❌ ما قدرتش نرسل الخط. التأكد من الرابط. الخطأ: `{e}`",
            ephemeral=True,
        )

@bot.tree.command(name="say", description="إرسال رسالة داخل Embed في الشات")
@discord.app_commands.describe(
    message="النص المراد كتابته داخل الـ Embed",
    image_url="رابط الصورة المراد إرفاقها (اختياري)",
)
@check_roles(SAY_ROLES)
async def say_embed(interaction: discord.Interaction, message: str, image_url: str = None):
    try:
        embed = discord.Embed(description=message, color=discord.Color.blue())
        if image_url:
            embed.set_image(url=image_url)

        await interaction.channel.send(embed=embed)
        await interaction.response.send_message(
            "✅ تم إرسال الرسالة بنجاح!", ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(
            f"❌ حدث خطأ أثناء إرسال الرسالة: `{e}`", ephemeral=True
        )

@bot.tree.command(name="bc", description="إرسال إعلان لشات معين مع صورة")
@discord.app_commands.describe(
    channel="الشات المراد الإرسال فيه",
    message="نص الإعلان",
    title="عنوان الإعلان (اختياري)",
    image_url="رابط الصورة (اختياري)",
)
@check_roles(BC_ROLES)
async def broadcast_channel(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    message: str,
    title: str = None,
    image_url: str = None,
):
    try:
        embed = discord.Embed(title=title, description=message, color=discord.Color.gold())
        embed.set_footer(text=f"Sent by {interaction.user.display_name}")

        if image_url:
            embed.set_image(url=image_url)

        await channel.send(embed=embed)
        await interaction.response.send_message(
            f"✅ تم الإرسال في {channel.mention} بنجاح!", ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(
            f"❌ خطأ: `{e}`", ephemeral=True
        )

@bot.tree.command(name="bc_dm", description="إرسال إعلان لجميع أعضاء السيرفر في الخاص")
@discord.app_commands.describe(message="نص الإعلان المراد إرساله")
@check_roles(BC_ROLES)
async def broadcast_dm(interaction: discord.Interaction, message: str):
    members = [m for m in interaction.guild.members if not m.bot]

    await interaction.response.send_message(
        f"⏳ جاري الإرسال إلى **{len(members)}** عضو في الخاص...",
        ephemeral=True,
    )

    success = 0
    failed_dm_closed = 0
    failed_other = 0
    last_error_msg = ""

    embed = discord.Embed(
        title=f"🔔 إعلان من {interaction.guild.name}",
        description=message,
        color=discord.Color.blue(),
    )

    for member in members:
        try:
            user = await bot.fetch_user(member.id)
            await user.send(embed=embed)
            success += 1
            await asyncio.sleep(2.0)
        except discord.Forbidden as e:
            failed_dm_closed += 1
            last_error_msg = f"Forbidden (50007): {e}"
        except discord.HTTPException as e:
            failed_other += 1
            last_error_msg = f"HTTP Error {e.status}: {e.text}"
            if e.status == 429:
                retry_after = int(e.response.headers.get("Retry-After", 5))
                await asyncio.sleep(retry_after)
        except Exception as e:
            failed_other += 1
            last_error_msg = str(e)

    result_text = (
        f"✅ **اكتمل الإرسال!**\n"
        f"📥 **نجح:** `{success}`\n"
        f"🚫 **فشل (سادين الـ DM / ممنوع):** `{failed_dm_closed}`\n"
        f"❌ **فشل (أخطاء أخرى):** `{failed_other}`"
    )

    if success == 0:
        result_text += f"\n\n⚠️ **تفاصيل الخطأ:**\n`{last_error_msg}`\n💡 *تأكد من تفعيل Server Members Intent فـ Discord Developer Portal!*"

    await interaction.edit_original_response(content=result_text)

class ConfirmDeleteAll(discord.ui.View):
    def __init__(self, author: discord.Member):
        super().__init__(timeout=30)
        self.author = author

    @discord.ui.button(
        label="تأكيد الحذف", style=discord.ButtonStyle.danger, emoji="🗑️"
    )
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user != self.author:
            await interaction.response.send_message(
                "❌ ليس مسموحاً لك استخدام هذا الزر.", ephemeral=True
            )
            return

        await interaction.response.edit_message(
            content="⏳ جاري مسح جميع رسائل الروم...", view=None
        )
        try:
            deleted = await interaction.channel.purge(limit=None)
            temp_msg = await interaction.channel.send(
                f"✅ تم مسح `{len(deleted)}` رسالة بنجاح!"
            )
            await asyncio.sleep(3)
            await temp_msg.delete()
        except Exception as e:
            await interaction.followup.send(
                f"❌ حدث خطأ أثناء الحذف: {e}", ephemeral=True
            )

    @discord.ui.button(
        label="إلغاء", style=discord.ButtonStyle.secondary, emoji="❌"
    )
    async def cancel(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user != self.author:
            await interaction.response.send_message(
                "❌ ليس مسموحاً لك استخدام هذا الزر.", ephemeral=True
            )
            return
        await interaction.response.edit_message(
            content="❌ تم إلغاء عملية الحذف.", view=None
        )

@bot.tree.command(name="ms7", description="مسح جميع الرسائل في الروم الحالية")
@discord.app_commands.checks.has_permissions(manage_messages=True)
async def ms7_all(interaction: discord.Interaction):
    view = ConfirmDeleteAll(interaction.user)
    await interaction.response.send_message(
        "⚠️ **هل أنت متأكد من أنك تريد حذف جميع رسائل هذه الروم؟**",
        view=view,
        ephemeral=True,
    )

@bot.tree.command(
    name="ms7_count",
    description="مسح عدد محدد من الرسائل فوق رسالة الأمر",
)
@discord.app_commands.describe(count="عدد الرسائل المراد حذفها")
@discord.app_commands.checks.has_permissions(manage_messages=True)
async def mss7_count(interaction: discord.Interaction, count: int):
    if count <= 0:
        await interaction.response.send_message(
            "❌ يرجى إدخال عدد أكبر من 0.", ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)
    try:
        deleted = await interaction.channel.purge(limit=count)
        temp_msg = await interaction.channel.send(
            f"✅ تم مسح `{len(deleted)}` رسالة بنجاح!"
        )
        await asyncio.sleep(3)
        await temp_msg.delete()
    except Exception as e:
        await interaction.followup.send(f"❌ حدث خطأ: {e}", ephemeral=True)

@bot.tree.command(name="7l", description="فتح الروم لتسمح للأعضاء بالكتابة فيها")
@discord.app_commands.checks.has_permissions(manage_channels=True)
async def open_channel(interaction: discord.Interaction):
    try:
        await interaction.channel.set_permissions(
            interaction.guild.default_role, send_messages=True
        )
        await interaction.response.send_message("🔓 تم فتح الروم بنجاح!")
    except Exception as e:
        await interaction.response.send_message(f"❌ حدث خطأ: {e}", ephemeral=True)

# ---------------------------------------------------------
# Running Bot
# ---------------------------------------------------------
token = os.getenv("TOKEN")
if not token:
    raise ValueError("❌ لم يتم العثور على التوكن! تأكد أن اسم المتغير في Railway هو TOKEN")

bot.run(token)
