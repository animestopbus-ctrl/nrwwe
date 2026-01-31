# Settings Module
# Rexbots - Don't Remove Credit
# Telegram Channel: @RexBots_Official

import os
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db import db
from Rexbots.strings import COMMANDS_TXT

@Client.on_message(filters.command("settings") & filters.private)
async def settings_menu(client: Client, message: Message):
    user_id = message.from_user.id
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)

    is_premium = await db.check_premium(user_id)
    badge = "💎 Premium Member" if is_premium else "👤 Free User"

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📜 Commands List", callback_data="cmd_list_btn")],
        [InlineKeyboardButton("📊 My Usage Stats", callback_data="user_stats_btn")],
        [InlineKeyboardButton("🗑 Dump Chat", callback_data="dump_chat_btn")],
        [InlineKeyboardButton("🖼 Thumbnail", callback_data="thumb_btn"),
         InlineKeyboardButton("📝 Caption", callback_data="caption_btn")],
        [InlineKeyboardButton("❌ Close", callback_data="close_btn")]
    ])

    text = (
        f"<b>⚙️ Settings Panel</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>Account:</b> {badge}\n"
        f"<b>User ID:</b> <code>{user_id}</code>\n\n"
        f"<i>Customize your experience below.</i>"
    )
    await message.reply_text(text, reply_markup=buttons, parse_mode=enums.ParseMode.HTML)

@Client.on_callback_query(filters.regex("^(cmd_list_btn|user_stats_btn|dump_chat_btn|thumb_btn|caption_btn|settings_back_btn|close_btn)$"))
async def settings_callbacks(client: Client, callback_query: CallbackQuery):
    data = callback_query.data
    user_id = callback_query.from_user.id
    back_close = [[InlineKeyboardButton("⬅️ Back", callback_data="settings_back_btn"), InlineKeyboardButton("❌ Close", callback_data="close_btn")]]

    if data == "cmd_list_btn":
        await callback_query.edit_message_text(
            COMMANDS_TXT,
            reply_markup=InlineKeyboardMarkup(back_close),
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )

    elif data == "user_stats_btn":
        is_premium = await db.check_premium(user_id)
        user_data = await db.col.find_one({'id': user_id}) or {}
        usage = user_data.get('daily_usage', 0)
        text = (
            f"<b>📊 My Usage Statistics</b>\n\n"
            f"<b>Plan:</b> {'💎 Premium' if is_premium else '👤 Free'}\n"
            f"<b>Daily Limit:</b> {'♾️ Unlimited' if is_premium else '10 files'}\n"
            f"<b>Today's Usage:</b> <code>{usage}{' (Ignored)' if is_premium else f'/{10}'}</code>"
        )
        await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(back_close), parse_mode=enums.ParseMode.HTML)

    elif data == "settings_back_btn":
        await settings_menu(client, callback_query.message)

    elif data == "close_btn":
        await callback_query.message.delete()

    await callback_query.answer()
