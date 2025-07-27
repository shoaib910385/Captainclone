import asyncio
import os
from datetime import datetime, timedelta
from typing import Union

from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.exceptions import (
    AlreadyJoinedError,
    NoActiveGroupCall,
    TelegramServerError,
)
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio, MediumQualityVideo

import config
from Clonify import LOGGER
from Clonify.utils.database import (
    add_active_chat,
    remove_active_chat,
    group_assistant,
)

class Call:
    def __init__(self):
        self.userbot1 = Client(
            name="RAUSHANAss1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
        )
        self.one = PyTgCalls(self.userbot1, cache_duration=150)

    async def start(self):
        await self.userbot1.start()
        await self.one.start()
        LOGGER(__name__).info("Userbot and PyTgCalls started successfully.")

    async def join_stream(self, chat_id: int, file_path: str, video: bool = False):
        assistant = self.one
        try:
            if video:
                stream = AudioVideoPiped(
                    file_path,
                    audio_parameters=HighQualityAudio(),
                    video_parameters=MediumQualityVideo(),
                )
            else:
                stream = AudioPiped(file_path, HighQualityAudio())
            await assistant.join_group_call(
                chat_id,
                stream,
                stream_type=StreamType().pulse_stream,
            )
            await add_active_chat(chat_id)
        except AlreadyJoinedError:
            await assistant.leave_group_call(chat_id)
            await asyncio.sleep(2)
            return await self.join_stream(chat_id, file_path, video)
        except NoActiveGroupCall:
            LOGGER(__name__).error(f"No active voice chat in {chat_id}")
        except TelegramServerError:
            LOGGER(__name__).error("Telegram server error")

    async def leave_stream(self, chat_id: int):
        try:
            await self.one.leave_group_call(chat_id)
        except:
            pass
        await remove_active_chat(chat_id)

    async def pause_stream(self, chat_id: int):
        await self.one.pause_stream(chat_id)

    async def resume_stream(self, chat_id: int):
        await self.one.resume_stream(chat_id)
