import asyncio

from pyrogram import Client, filters, __version__ as pyrover
from pyrogram.errors import FloodWait, UserNotParticipant
from pytgcalls import (__version__ as pytover)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, ChatJoinRequest
from m8n.utils.filters import command

from m8n.config import BOT_USERNAME
from m8n.config import START_PIC
from m8n.config import BOT_NAME



@Client.on_message(command("start") & filters.private & ~filters.edited)
async def start_(client: Client, message: Message):
     await message.reply_sticker("CAADBQAD-QQAAhCWOFRERrHKHtIUvgI")
     await message.reply_text(
           f"""**✌️ɪᴍ ʟᴀᴢʏ ᴀʙᴏᴜᴛ ᴛʏᴘɪɴɢ ᴀɴʏᴛʜɪɴɢ ɪᴛs ᴀ ᴍᴜsɪᴄ ʙᴏᴛ ʜᴀᴠᴇ ᴍᴀɴʏ ғᴇᴀᴛᴜʀᴇs📍\n\n ᴄʀᴇᴀᴛᴇᴅ ʙʏ[s•4•sʜɪᴠ](t.me/shivamdemon)...
"""
    reply_markup=InlineKeyboardMarkup(
            [
                [   
                    InlineKeyboardButton(
                        "💜°ᴏᴡɴᴇʀ°", url=f"https://t.me/itz_rupu")
                ],
                [
                    InlineKeyboardButton(
                        "💫ɢʀᴏᴜᴘ", callback_data="squadgoalsss"),
                    InlineKeyboardButton(
                        "°⚙️ᴄᴍᴅs°", callback_data="cbcmds")
                ],
                [
                    InlineKeyboardButton(
                        "🏷️°sᴜᴍᴍᴏɴ ᴍᴇ ʙᴀʙʏ°", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")
                ]
           ]
        ),
    )


@Client.on_message(command(["start"]) & filters.group & ~filters.edited)
async def help(client: Client, message: Message):
    await message.reply_photo(
        photo=f"{START_PIC}",
        caption=f"""ᴛʜᴀɴᴋs ғᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ 🔥♥️""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "°ᴏᴡɴᴇʀ° 💞", url=f"https://t.me/itz_rupu"),
                    InlineKeyboardButton(
                        "°sᴜᴘᴘᴏʀᴛᴇʀ° ✨", url=f"https://t.me/shivamdemon")
                ]
            ]
        ),
    )
