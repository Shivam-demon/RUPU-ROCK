import aiofiles
import ffmpeg
import asyncio
import os
import shutil
import psutil
import subprocess
import requests
import aiohttp
import yt_dlp

from os import path
from typing import Union
from asyncio import QueueEmpty
from PIL import Image, ImageFont, ImageDraw
from typing import Callable

from pytgcalls import StreamType
from pytgcalls.types.input_stream import InputStream
from pytgcalls.types.input_stream import InputAudioStream

from youtube_search import YoutubeSearch

from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    Voice,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
)
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant

from m8n.tgcalls import calls, queues
from m8n.tgcalls.calls import client as ASS_ACC
from m8n.database.queue import (
    get_active_chats,
    is_active_chat,
    add_active_chat,
    remove_active_chat,
    music_on,
    is_music_playing,
    music_off,
)
from m8n import app
import m8n.tgcalls
from m8n.tgcalls import youtube
from m8n.config import (
    DURATION_LIMIT,
    que,
    SUDO_USERS,
    BOT_ID,
    ASSNAME,
    ASSUSERNAME,
    ASSID,
    SUPPORT,
    UPDATE,
    BOT_USERNAME,
)
from m8n.utils.filters import command
from m8n.utils.decorators import errors, sudo_users_only
from m8n.utils.administrator import adminsOnly
from m8n.utils.errors import DurationLimitError
from m8n.utils.gets import get_url, get_file_name
from m8n.modules.admins import member_permissions


# plus
chat_id = None
DISABLED_GROUPS = []
useer = "NaN"
flex = {}


def transcode(filename):
    ffmpeg.input(filename).output(
        "input.raw", format="s16le", acodec="pcm_s16le", ac=2, ar="48k"
    ).overwrite_output().run()
    os.remove(filename)


# Convert seconds to mm:ss
def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


# Convert hh:mm:ss to seconds
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))


# Change image size
def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    return image.resize((newWidth, newHeight))


async def generate_cover(requested_by, title, views, duration, thumbnail):
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                f = await aiofiles.open("background.png", mode="wb")
                await f.write(await resp.read())
                await f.close()

    image1 = Image.open("./background.png")
    image2 = Image.open("etc/foreground.png")
    image3 = changeImageSize(1280, 720, image1)
    image4 = changeImageSize(1280, 720, image2)
    image5 = image3.convert("RGBA")
    image6 = image4.convert("RGBA")
    Image.alpha_composite(image5, image6).save("temp.png")
    img = Image.open("temp.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("etc/font.otf", 32)
    draw.text((190,550), f"Now playing", (255, 255, 255), font=font)
    draw.text((190, 590), f"Title: {title}", (255, 255, 255), font=font)
    
    img.save("final.png")
    os.remove("temp.png")
    os.remove("background.png")


@Client.on_message(
    command(["musicplayer", f"musicplayer@{BOT_USERNAME}"])
    & ~filters.edited
    & ~filters.bot
    & ~filters.private
)
async def hfmm(_, message):
    global DISABLED_GROUPS
    if message.sender_chat:
        return await message.reply_text(
            "🐬 ʏᴏᴜ ᴀʀᴇ **ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ**!│\nᴛʀʏ ᴡɪᴛʜ ᴜʀ ᴀᴅᴍɪɴ ᴀᴄᴄᴏᴜɴᴛ."
        )
    permission = "can_delete_messages"
    m = await adminsOnly(permission, message)
    if m == 1:
        return
    try:
        user_id = message.from_user.id
    except:
        return
    if len(message.command) != 2:
        await message.reply_text("ɪ ᴏɴʟʏ ᴋɴᴏᴡ `/musicplayer on` & `/musicplayer off`")
        return
    status = message.text.split(None, 1)[1]
    message.chat.id
    if status in ["ON", "on", "On"]:
        lel = await message.reply("`Processing...`")
        if message.chat.id not in DISABLED_GROUPS:
            await lel.edit(
                f"💤 ᴠᴄ ᴘʟᴀʏᴇʀ ɪs ᴀᴄᴛɪᴠᴀᴛᴇᴅ ɪɴ **{message.chat.title}**"
            )
            return
        DISABLED_GROUPS.remove(message.chat.id)
        await lel.edit(
            f"🎵 ᴠᴄ ᴘʟᴀʏᴇʀ ɪs sᴜᴄᴄᴇsғᴜʟʟʏ ᴛᴜʀɴ ᴏɴ ɪɴ **{message.chat.title}**"
        )

    elif status in ["OFF", "off", "Off"]:
        lel = await message.reply("__`ᴘʀᴏᴄᴇssɪɴɢ...`")

        if message.chat.id in DISABLED_GROUPS:
            await lel.edit(
                f"💤 ᴠᴄ ᴘʟᴀʏᴇʀ ɪs ɴᴏᴛ ᴀᴄᴛɪᴠᴇ ɪɴ **{message.chat.title}**"
            )
            return
        DISABLED_GROUPS.append(message.chat.id)
        await lel.edit(
            f"🎵 ᴠᴄ ᴘʟᴀʏᴇʀ ɪs sᴜᴄᴄᴇsғᴜʟʟʏ ᴛᴜʀɴ ᴏғғ ɪɴ **{message.chat.title}**"
        )
    else:
        await message.reply_text("ɪ ᴏɴʟʏ ᴋɴᴏᴡ `/musicplayer on` & `/musicplayer off`")


@Client.on_callback_query(filters.regex(pattern=r"^(cls)$"))
async def closed(_, query: CallbackQuery):
    from_user = query.from_user
    permissions = await member_permissions(query.message.chat.id, from_user.id)
    permission = "can_restrict_members"
    if permission not in permissions:
        return await query.answer(
            "ʏᴏᴜ ᴅᴏɴᴛʜᴀᴠᴇ ᴇɴᴏᴜɢʜ ᴀᴅᴍɪɴ ʀɪɢʜᴛs.\n"
            + f"❌ ᴘᴇʀᴍɪssɪᴏɴ: {permission}",
            show_alert=True,
        )
    await query.message.delete()


# play
@Client.on_message(
    command(["play", f"play@{BOT_USERNAME}"])
    & filters.group
    & ~filters.edited
    & ~filters.forwarded
    & ~filters.via_bot
)
async def play(_, message: Message):
    global que
    global useer
    user_id = message.from_user.id
    if message.sender_chat:
        return await message.reply_text(
            "🐬 ʏᴏᴜ ᴀʀᴇ **ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ**!│\nᴛʀʏ ᴡɪᴛʜ ᴜʀ ᴀᴅᴍɪɴ ᴀᴄᴄᴏᴜɴᴛ."
        )

    if message.chat.id in DISABLED_GROUPS:
        await message.reply(
            "🏷️ **ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ɪs ᴏғғ ᴀsᴋ ᴀᴅᴍɪɴ ᴛᴏ ᴛᴜʀɴ ɪᴛ ᴏɴ!**__"
        )
        return
    lel = await message.reply("🔄 **ᴘʀᴏᴄᴇssɪɴɢ...**")

    chid = message.chat.id

    c = await app.get_chat_member(message.chat.id, BOT_ID)
    if c.status != "administrator":
        await lel.edit(
            f"**ᴛᴏ ᴇɴᴊᴏʏ sᴇᴇᴍʟᴇss ᴍᴜsɪᴄ ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ ғɪʀsᴛ.💜💫"
        )
        return
    if not c.can_manage_voice_chats:
        await lel.edit(
            "ᴅᴏɴᴛ ʜᴀᴠᴇ ʀɪɢʜᴛ ɢɪᴠᴇ ᴍᴇ."
            + "\n💡 **ᴘᴇʀᴍɪssɪᴏɴ:** Manage Voice Chats"
        )
        return
    if not c.can_delete_messages:
        await lel.edit(
            "ᴅᴏɴᴛ ʜᴀᴠᴇ ʀɪɢʜᴛ ɢɪᴠᴇ ᴍᴇ."
            + "\n💡 **ᴘᴇʀᴍɪssɪᴏɴ:** Delete Message"
        )
        return
    if not c.can_invite_users:
        await lel.edit(
            "ᴅᴏɴᴛ ʜᴀᴠᴇ ʀɪɢʜᴛ ɢɪᴠᴇ ᴍᴇ."
            + "\n💡 **ᴘᴇʀᴍɪssɪᴏɴ:** Invite User Via Invitelink"
        )
        return

    try:
        b = await app.get_chat_member(message.chat.id, ASSID)
        if b.status == "kicked":
            await message.reply_text(
                f"🏷️ {ASSNAME} (@{ASSUSERNAME}) ʙᴀɴɴᴇᴅ ɪɴ ᴛʜɪs ᴄʜᴀᴛ **{message.chat.title}**\n\nᴜɴʙᴀɴ ғɪʀsᴛ ᴛᴏ ᴀᴅᴅ ɪᴛ🐬"
            )
            return
    except UserNotParticipant:
        if message.chat.username:
            try:
                await ASS_ACC.join_chat(f"{message.chat.username}")
                await message.reply(
                    f"💫 **ᴀssɪsᴛᴀɴᴛ ᴊᴏɪɴᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ...💜🥀**",
                )
                await remove_active_chat(chat_id)
            except Exception as e:
                await message.reply_text(
                    f"❌ **ᴀssɪsᴛᴀɴᴛ ғᴀɪʟᴇᴅ ᴛᴏ ᴊᴏɪɴ🥺**\n**💭Reason**:{e}"
                )
                return
        else:
            try:
                invite_link = await message.chat.export_invite_link()
                if "+" in invite_link:
                    kontol = (invite_link.replace("+", "")).split("t.me/")[1]
                    link_bokep = f"https://t.me/joinchat/{kontol}"
                await ASS_ACC.join_chat(link_bokep)
                await message.reply(
                    f"💫 **ᴀssɪsᴛᴀɴᴛ ᴊᴏɪɴᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ...💜🥀**",
                )
                await remove_active_chat(message.chat.id)
            except UserAlreadyParticipant:
                pass
            except Exception as e:
                return await message.reply_text(
                    f"❌ **ᴀssɪsᴛᴀɴᴛ ғᴀɪʟᴇᴅ ᴛᴏ ᴊᴏɪɴ🥺**\n**💭Reason**:{e}"
                )

    await message.delete()
    audio = (
        (message.reply_to_message.audio or message.reply_to_message.voice)
        if message.reply_to_message
        else None
    )
    url = get_url(message)

    if audio:
        if round(audio.duration / 60) > DURATION_LIMIT:
            raise DurationLimitError(
                f"⭕ ʏᴏᴜʀ ᴄʜᴏɪᴄᴇ ɪs ʟᴏɴɢᴇʀ ᴛʜᴀɴ {DURATION_LIMIT} ᴍɪɴᴜᴛᴇs💜✌️!"
            )

        file_name = get_file_name(audio)
        url = f"https://t.me/{UPDATE}"
        title = audio.title
        thumb_name = "https://telegra.ph/file/22e0f6fd383b078132fd0.jpg"
        thumbnail = thumb_name
        duration = round(audio.duration / 60)
        views = "Locally added"

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("😴°ɢʀᴏᴜᴘ°", url=f"https://t.me/squadgoalsss"),
                ],
            ]
        )

        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await m8n.tgcalls.convert(
            (await message.reply_to_message.download(file_name))
            if not path.isfile(path.join("downloads", file_name))
            else file_name
        )

    elif url:
        try:
            results = YoutubeSearch(url, max_results=1).to_dict()
            # print results
            title = results[0]["title"]
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f"thumb{title}.jpg"
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, "wb").write(thumb.content)
            duration = results[0]["duration"]
            url_suffix = results[0]["url_suffix"]
            views = results[0]["views"]
            durl = url
            durl = durl.replace("youtube", "youtubepp")

            secmul, dur, dur_arr = 1, 0, duration.split(":")
            for i in range(len(dur_arr) - 1, -1, -1):
                dur += int(dur_arr[i]) * secmul
                secmul *= 60

            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("😴°ɢʀᴏᴜᴘ°", url=f"https://t.me/squadgoalsss"),
                    ],
                ]
            )

        except Exception as e:
            title = "NaN"
            thumb_name = "https://telegra.ph/file/22e0f6fd383b078132fd0.jpg"
            duration = "NaN"
            views = "NaN"
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="YouTube 🎬", url="https://youtube.com")]]
            )

        if (dur / 60) > DURATION_LIMIT:
            await lel.edit(
                f"⭕ ʏᴏᴜʀ ᴄʜᴏɪᴄᴇ ɪs ʟᴏɴɢᴇʀ ᴛʜᴀɴ {DURATION_LIMIT} ᴍɪɴᴜᴛᴇs💜✌️!"
            )
            return
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)

        def my_hook(d):
            if d["status"] == "downloading":
                percentage = d["_percent_str"]
                per = (str(percentage)).replace(".", "", 1).replace("%", "", 1)
                per = int(per)
                eta = d["eta"]
                speed = d["_speed_str"]
                size = d["_total_bytes_str"]
                bytesx = d["total_bytes"]
                if str(bytesx) in flex:
                    pass
                else:
                    flex[str(bytesx)] = 1
                if flex[str(bytesx)] == 1:
                    flex[str(bytesx)] += 1
                    try:
                        if eta > 2:
                            lel.edit(
                                f"▷ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ{title[:50]}\n\n*sɪᴢᴇ:** {size}\n**ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ:** {percentage}\n**sᴘᴇᴇᴅ:** {speed}\n**ᴇᴛᴀ:** {eta} sec"
                            )
                    except Exception as e:
                        pass
                if per > 250:
                    if flex[str(bytesx)] == 2:
                        flex[str(bytesx)] += 1
                        if eta > 2:
                            lel.edit(
                                f"**▷ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ** {title[:50]}..\n\n**sɪᴢᴇ:** {size}\n**ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ:** {percentage}\n**sᴘᴇᴇᴅ:** {speed}\n**ᴇᴛᴀ:** {eta} sec"
                            )
                        print(
                            f"[{url_suffix}] sᴀᴠᴇᴅ {percentage} ᴡɪᴛʜ sᴘᴇᴇᴅ {speed} | ᴇᴛᴀ: {eta} seconds"
                        )
                if per > 500:
                    if flex[str(bytesx)] == 3:
                        flex[str(bytesx)] += 1
                        if eta > 2:
                            lel.edit(
                                f"**▷ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ** {title[:50]}...\n\n**sɪᴢᴇ:** {size}\n**ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ:** {percentage}\n**sᴘᴇᴇᴅ:** {speed}\n**ᴇᴛᴀ:** {eta} sec"
                            )
                        print(
                            f"[{url_suffix}] sᴀᴠᴇᴅ {percentage} ᴡɪᴛʜ sᴘᴇᴇᴅ {speed} | ᴇᴛᴀ: {eta} seconds"
                        )
                if per > 800:
                    if flex[str(bytesx)] == 4:
                        flex[str(bytesx)] += 1
                        if eta > 2:
                            lel.edit(
                                f"**▷ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ** {title[:50]}....\n\n**sɪᴢᴇ:** {size}\n**ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ:** {percentage}\n**sᴘᴇᴇᴅ:** {speed}\n**ᴇᴛᴀ:** {eta} sec"
                            )
                        print(
                            f"[{url_suffix}] sᴀᴠᴇᴅ {percentage} ᴡɪᴛʜ sᴘᴇᴇᴅ {speed} | ᴇᴛᴀ: {eta} seconds"
                        )
            if d["status"] == "finished":
                try:
                    taken = d["_elapsed_str"]
                except Exception as e:
                    taken = "00:00"
                size = d["_total_bytes_str"]
                lel.edit(
                    f"**▷ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ** {title[:50]}.....\n\n**sɪᴢᴇ:** {size}\n**ᴛɪᴍᴇ ᴜᴘᴛᴏ:** {taken} sec\n\n**ᴄᴏɴᴠᴇʀᴛᴇᴅ ᴛᴏ**[__FFmpeg processing__]"
                )
                print(f"[{url_suffix}] Downloaded| ɪɴᴛᴇʀᴠᴀʟ: {taken} seconds")

        loop = asyncio.get_event_loop()
        x = await loop.run_in_executor(None, youtube.download, url, my_hook)
        file_path = await m8n.tgcalls.convert(x)
    else:
        if len(message.command) < 2:
            return await lel.edit(
                "⭕ **ғᴏᴜɴᴅ ɴᴏᴛʜɪɴɢ!! ᴛʀʏ ᴀɢᴀɪɴ ᴡɪᴛʜ ᴄᴏʀʀᴇᴄᴛ sᴘᴇʟʟ💜✌️**"
            )
        await lel.edit("🔎 **ғᴏᴜɴᴅ sᴏᴍᴇᴛʜɪɴɢ...**")
        query = message.text.split(None, 1)[1]
        # print(query)
        await lel.edit("**ᴊᴏɪɴɪɴɢ ᴠᴄ... !!**")
        try:
            results = YoutubeSearch(query, max_results=5).to_dict()
            url = f"https://youtube.com{results[0]['url_suffix']}"
            # print results
            title = results[0]["title"]
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f"thumb{title}.jpg"
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, "wb").write(thumb.content)
            duration = results[0]["duration"]
            url_suffix = results[0]["url_suffix"]
            views = results[0]["views"]
            durl = url
            durl = durl.replace("youtube", "youtubepp")

            secmul, dur, dur_arr = 1, 0, duration.split(":")
            for i in range(len(dur_arr) - 1, -1, -1):
                dur += int(dur_arr[i]) * secmul
                secmul *= 60

        except Exception as e:
            await lel.edit(
                "💭💜 ғᴏᴜɴᴅ ɴᴏᴛʜɪɴɢ ᴛʀʏ ᴏɴᴄᴇ ᴍᴏʀᴇ ᴏʀ `/play [yt url]`."
            )
            print(str(e))
            return

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("😴°ɢʀᴏᴜᴘ°", url=f"https://t.me/squadgoalsss"),
                ],
            ]
        )

        if (dur / 60) > DURATION_LIMIT:
            await lel.edit(
                f"❌ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ʟᴏɴɢᴇʀ ᴛʜᴀɴ {DURATION_LIMIT} ᴍɪɴᴜᴛᴇs💜!"
            )
            return
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)

        def my_hook(d):
            if d["status"] == "downloading":
                percentage = d["_percent_str"]
                per = (str(percentage)).replace(".", "", 1).replace("%", "", 1)
                per = int(per)
                eta = d["eta"]
                speed = d["_speed_str"]
                size = d["_total_bytes_str"]
                bytesx = d["total_bytes"]
                if str(bytesx) in flex:
                    pass
                else:
                    flex[str(bytesx)] = 1
                if flex[str(bytesx)] == 1:
                    flex[str(bytesx)] += 1
                    try:
                        if eta > 2:
                            lel.edit(
                                f"▷ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ {title[:50]}\n\n**sɪᴢᴇ:** {size}\n**ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ:** {percentage}\n**sᴘᴇᴇᴅ:** {speed}\n**ᴇᴛᴀ:** {eta} sec"
                            )
                    except Exception as e:
                        pass
                if per > 250:
                    if flex[str(bytesx)] == 2:
                        flex[str(bytesx)] += 1
                        if eta > 2:
                            lel.edit(
                                f"**▷ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ** {title[:50]}..\n\n**sɪᴢᴇ:** {size}\n**ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ:** {percentage}\n**sᴘᴇᴇᴅ:** {speed}\n**ᴇᴛᴀ:** {eta} sec"
                            )
                        print(
                            f"[{url_suffix}] sᴀᴠᴇᴅ {percentage} ᴡɪᴛʜ sᴘᴇᴇᴅ {speed} | ᴇᴛᴀ: {eta} seconds"
                        )
                if per > 500:
                    if flex[str(bytesx)] == 3:
                        flex[str(bytesx)] += 1
                        if eta > 2:
                            lel.edit(
                                f"**▷ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ** {title[:50]}...\n\n**sɪᴢᴇ:** {size}\n**ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ:** {percentage}\n**sᴘᴇᴇᴅ:** {speed}\n**ᴇᴛᴀ:** {eta} sec"
                            )
                        print(
                            f"[{url_suffix}] sᴀᴠᴇᴅ {percentage} ᴡɪᴛʜ sᴘᴇᴇᴅ {speed} | ᴇᴛᴀ: {eta} seconds"
                        )
                if per > 800:
                    if flex[str(bytesx)] == 4:
                        flex[str(bytesx)] += 1
                        if eta > 2:
                            lel.edit(
                                f"**▷ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ* {title[:50]}....\n\n**sɪᴢᴇ:** {size}\n**ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ:** {percentage}\n**sᴘᴇᴇᴅ:** {speed}\n**ᴇᴛᴀ:** {eta} sec"
                            )
                        print(
                            f"[{url_suffix}] sᴀᴠᴇᴅ {percentage} ᴡɪᴛʜ sᴘᴇᴇᴅ {speed} | ᴇᴛᴀ: {eta} seconds"
                        )
            if d["status"] == "finished":
                try:
                    taken = d["_elapsed_str"]
                except Exception as e:
                    taken = "00:00"
                size = d["_total_bytes_str"]
                lel.edit(
                    f"**▷ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ** {title[:50]}.....\n\n**sɪᴢᴇ:** {size}\n**ᴛɪᴍᴇ ᴜᴘᴛᴏ:** {taken} sec\n\n**ᴄᴏɴᴠᴇʀᴛɪɴɢ**[__FFmpeg processing__]"
                )
                print(f"[{url_suffix}] sᴀᴠᴇᴅ| ɪɴᴛᴇʀᴠᴀʟ: {taken} seconds")

        loop = asyncio.get_event_loop()
        x = await loop.run_in_executor(None, youtube.download, url, my_hook)
        file_path = await m8n.tgcalls.convert(x)

    if await is_active_chat(message.chat.id):
        position = await queues.put(message.chat.id, file=file_path)
        await message.reply_photo(
            photo="final.png",
            caption="**✨ᴍᴜsɪᴄ:** {}\n\n⏱️ᴅᴜʀᴀᴛɪᴏɴ : {}\n🎧ᴜsᴇʀ : {}".format(
                title, duration, message.from_user.mention()
            ),
            reply_markup=keyboard,
        )
    else:
        try:
            await calls.pytgcalls.join_group_call(
                message.chat.id,
                InputStream(
                    InputAudioStream(
                        file_path,
                    ),
                ),
                stream_type=StreamType().local_stream,
            )
        except Exception:
            return await lel.edit(
                "ғᴀɪʟᴇᴅ ᴛᴏ ᴊᴏɪɴ ᴠᴄ.ᴛᴜʀɴ ᴏɴ ᴠᴄ💜."
            )

        await music_on(message.chat.id)
        await add_active_chat(message.chat.id)
        await message.reply_photo(
            photo="final.png",
            reply_markup=keyboard,
            caption="**✨ᴍᴜsɪᴄ:** {}\n\n⏱️ᴅᴜʀᴀᴛɪᴏɴ : {}\n🎧ᴜsᴇʀ : {}".format(
                title, duration, message.from_user.mention()
            ),
        )

    os.remove("final.png")
    return await lel.delete()
