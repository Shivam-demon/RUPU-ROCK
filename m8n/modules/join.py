import asyncio

from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, FloodWait

from m8n import app, ASSUSERNAME
from m8n.utils.decorators import sudo_users_only, errors
from m8n.utils.administrator import adminsOnly
from m8n.utils.filters import command
from m8n.tgcalls import client as USER


@app.on_message(
    command(["userbotjoin", "botjoin", "join"]) & ~filters.private & ~filters.bot
)
@errors
async def addchannel(client, message):
    if message.sender_chat:
        return await message.reply_text(
            "🐬 ʏᴏᴜ ᴀʀᴇ **ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ**!│\nᴛʀʏ ᴡɪᴛʜ ᴜʀ ᴀᴅᴍɪɴ ᴀᴄᴄᴏᴜɴᴛ."
        )
    permission = "can_delete_messages"
    m = await adminsOnly(permission, message)
    if m == 1:
        return
    chid = message.chat.id
    try:
        invite_link = await message.chat.export_invite_link()
        if "+" in invite_link:
            kontol = (invite_link.replace("+", "")).split("t.me/")[1]
            link_bokep = f"https://t.me/joinchat/{kontol}"
    except:
        await message.reply_text(
            "**ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ ғɪʀsᴛ😒**",
        )
        return

    try:
        user = await USER.get_me()
    except:
        user.first_name = f"{ASSUSERNAME}"

    try:
        await USER.join_chat(link_bokep)
    except UserAlreadyParticipant:
        await message.reply_text(
            f"🔴 **{user.first_name} ᴀʟʀᴇᴀᴅʏ ᴊᴏɪɴᴇᴅ ʙᴜᴅᴅʏ**",
        )
    except Exception as e:
        print(e)
        await message.reply_text(
            f"❌ __**ᴀssɪsᴛᴀɴᴛ ({user.first_name})  ғᴀɪʟᴇᴅ ᴛᴏ ᴊᴏɪɴ ᴜʀ ɢʀᴏᴜᴘ ғɪʀsᴛ ᴜɴʙᴀɴ ɪᴛ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ."
            f"\n\n» `ᴍᴀɴᴜᴀʟʟʏ ᴀᴅᴅ {user.first_name} ᴛᴏ ɢʀᴏᴜᴘ`",
        )
        return


@USER.on_message(filters.group & command(["userbotleave", "odaleave", "odaleft"]))
async def rem(USER, message):
    if message.sender_chat:
        return await message.reply_text(
            "🐬 ʏᴏᴜ ᴀʀᴇ **ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ**!│\nᴛʀʏ ᴡɪᴛʜ ᴜʀ ᴀᴅᴍɪɴ ᴀᴄᴄᴏᴜɴᴛ."
        )
    permission = "can_delete_messages"
    m = await adminsOnly(permission, message)
    if m == 1:
        return
    try:
        await USER.send_message(
            message.chat.id,
            "✅ ᴀssɪsᴛᴀɴᴛ ʟᴇғᴛ sᴜᴄᴄᴇsғᴜʟʟʏ",
        )
        await USER.leave_chat(message.chat.id)
    except:
        await message.reply_text(
            "❌ ᴀssɪsᴛᴀɴᴛ ғᴀʟɪᴇᴅ ᴛᴏ ʟᴇᴀᴠᴇ ᴄʜᴀᴛ ᴍᴀʏ ʙᴇ ɪᴛs ғʟᴏᴏᴅ ɴ ʟɪᴍɪᴛ ᴇʀʀᴏʀ ᴛʀʏ ᴀɢᴀɪɴ...🥺"
        )

        return


@app.on_message(command(["userbotleaveall", "leaveall"]))
@sudo_users_only
async def bye(client, message):
    left = 0
    sleep_time = 0.1
    lol = await message.reply("**ᴜsʀʀʙᴏᴛ ʟᴇᴀᴠɪɴɢ ᴀʟʟ ᴄʜᴀᴛs**\n\n`ʟᴏᴀᴅɪɴɢ...`")
    async for dialog in USER.iter_dialogs():
        try:
            await USER.leave_chat(dialog.chat.id)
            await asyncio.sleep(sleep_time)
            left += 1
        except FloodWait as e:
            await asyncio.sleep(int(e.x))
        except Exception:
            pass
    await lol.edit(f"🏃‍♂️ `ᴜsᴇʀʙᴏᴛ ʟᴇᴀᴠɪɴɢ...`\n\n» **ʟᴇғᴛ:** {left} chats.")
