from aiogram import F, Router, types
from aiogram.filters import ChatMemberUpdatedFilter, IS_MEMBER, IS_NOT_MEMBER, IS_ADMIN
from aiogram.types import Message
import app.db as db
from groq import Groq
from langdetect import detect, LangDetectException
import time


rt = Router()
user_languages = {}
client = Groq(api_key="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")


@rt.my_chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def chat_group_info(message: Message):
    chat_id = message.chat.id
    group_title = message.chat.title if message.chat.title else "Private Chat"
    chat_type = message.chat.type
    chat_username = message.chat.username if message.chat.username else "N/A"
    response = (
        f"Chat ID: {chat_id}\n"
        f"Chat Title: {group_title}\n"
        f"Chat Type: {chat_type}\n"
        f"Chat Username: {chat_username}\n"
    )
    group_id = chat_id
    await db.group_join(chat_id, group_title, chat_type, chat_username)
    print(response)



@rt.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def on_user_join(message: Message):
    chat_member = await message.bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
    await message.answer(f"🎉 Welcome to the Group,[{message.from_user.first_name}](https://t.me/@id{message.from_user.id})! 🎉 \nWe’re excited to have you here! This is a space for [brief description of the group’s purpose, e.g., sharing ideas, discussing topics, etc.]. Please take a moment to introduce yourself and let us know what you're interested in. Feel free to ask questions, share your thoughts, and connect with others. Let’s make this community great together!", parse_mode="Markdown")
    try:
        await db.new_member(message.chat.id, message.from_user.id, message.from_user.full_name, message.from_user.last_name, message.from_user.username, message.from_user.is_premium, message.from_user.is_bot, chat_member.status)
    except TypeError as e:
        print("Error add member")

@rt.message(~F.text.startswith("/"), F.chat.type.in_({"group", "supergroup"}))
async def detect_and_set_language(message: types.Message):
    chat_member = await message.bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
    try:
        await db.new_member(message.chat.id, message.from_user.id, message.from_user.full_name, message.from_user.last_name, message.from_user.username, message.from_user.is_premium, message.from_user.is_bot, chat_member.status)
    except TypeError:
        #if it's works just dont touch it pls :)
        pass

    chat_id = message.chat.id 
    lang_empty_check = db.check_lang(chat_id)
    bd_status = await db.bd_status(message.chat.id)

    if bd_status:
        client = Groq(api_key="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")
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Answer with True or False no other comments: Is {message.text} a insult.", 
                }
            ],
            model="llama3-8b-8192",
        )

        bad_bool = chat_completion.choices[0].message.content.lower() == "true"
        if bad_bool:
            bd_counter = await db.bd_allert(message.from_user.id)
            await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bd_sticker = await message.answer_sticker('CAACAgIAAxkBAAIEkGcmU11loDi101RvrehWTmdR1ZPWAAJhAwACKvI6B04UMBOeum4YNgQ')
            bd_allert = await message.answer(f"💢Your words may cause offense or distress to others.💢 \nTherefore, it is advisable to avoid using offensive language. \n`Bad words counter⁉️:` *{bd_counter}*", parse_mode='Markdown')
            time.sleep(5)
            await message.bot.delete_message(chat_id=message.chat.id, message_id=bd_allert.message_id)
            await message.bot.delete_message(chat_id=message.chat.id, message_id=bd_sticker.message_id)
            if bd_counter % 10 == 0:
                await message.answer_sticker('CAACAgIAAxkBAAIEk2cmVPWjlkESdOinWMyBoTF5sPfyAAJjAwACKvI6B-mF0YdfLFGDNgQ')
                await message.answer(f"""You have exceeded the limit
Please think about your behavior.
You lose the right of speach for: {bd_counter*1.20}min""")
                await message.bot.restrict_chat_member(
                    chat_id=message.chat.id,
                    user_id=message.from_user.id,
                    permissions={
                        "can_send_messages": False,  # Disable sending messages
                        "can_send_media_messages": False,  # Disable media sending
                        "can_send_polls": False,  # Disable sending polls
                        "can_send_other_messages": False,  # Disable other types of messages
                        "can_add_web_page_previews": False,  # Disable adding web page previews
                        "can_change_info": False,
                        "can_pin_messages": False,
                    }
                )
                time.sleep(bd_counter*1.20*60)
                await message.bot.restrict_chat_member(
                    chat_id=message.chat.id,
                    user_id=message.from_user.id,
                    permissions={
                        "can_send_messages": True,  # Disable sending messages
                        "can_send_media_messages": True,  # Disable media sending
                        "can_send_polls": True,  # Disable sending polls
                        "can_send_other_messages": True,  # Disable other types of messages
                        "can_add_web_page_previews": True,  # Disable adding web page previews
                    }
                )
                
                

    if lang_empty_check and not user_languages:
        user_languages.setdefault('counter', 0)
    elif lang_empty_check and user_languages['counter'] >= 16:
        sorted_counter = sorted(user_languages, key=user_languages.get, reverse=True)
        second_largest_key = sorted_counter[1]
        print("\n")
        print("*****************************************************************")
        print(f'*      Group with id {chat_id} use mostly {second_largest_key} language      *')
        print("*****************************************************************")
        print("\n")
        try:
            await db.check_and_update_group_lang(chat_id, second_largest_key)
        except TypeError:
            print("Language successfuly updated")
            user_languages.clear()
        return

    elif not lang_empty_check:
        return
    
    try:
        detected_language = detect(message.text)
        user_languages['counter'] += 1
        user_languages.setdefault(str(detected_language), 0)
        user_languages[str(detected_language)] += 1
    except LangDetectException:
        # Handle the case where language detection fails
        await message.reply("Sorry, I couldn't detect the language.")


@rt.message(F.sticker)
async def stick_id(message: Message):
    if message.chat.id == message.from_user.id:
        await message.reply(message.sticker.file_id)
        await message.answer(f"group id: {message.chat.id}")
