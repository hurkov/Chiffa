import gtts, time, os, asyncio, requests
from aiogram import F, Router, types, methods

from aiogram.filters import Command, CommandStart
import app.db as db
import app.keyboards as kb
from groq import Groq
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

rtc = Router()
#8cb62e2091eacf46efdcdbf49a83b14a
#ATTAc42b19766273ea896faf0f11b3e0f4c10973a2b6a09f744985a5fca38c181e0669038ED2
#1002303379680


class Ser(StatesGroup):
    group_id = State()
    user_id = State()
    mailing = State()
    message_details = State()  # New state for capturing message details
    find_banned_member = State()
    promo_type = State()
    promo_content = State()
    promo_interval = State()
    change_status = State()
    trello_api_key = State()
    token = State()
    api_key = State()
    board = State()
    
group_id = None
banned_users = []
current_index = 0
promotion_task = None
mailing_task = None
status = None

@rtc.message(CommandStart())
async def cmd_start(message: types.Message):
    if message.chat.id == message.from_user.id:
        await message.answer_sticker('CAACAgIAAxkBAAODZyTqz7KosQcThNn1RUEziMFrVEUAAlQDAAIq8joHyM_lELQguOo2BA', reply_markup=kb.main)
        
        await message.answer(f"""`Hi I'm` *Chiffa*
I’m here to help keep groups safe, organized, and friendly! Here’s what I can do for you:
    
*🪄 Let's Start:*\n
*Add me ia a Supergroup* and promote me as *Admin* to let me get in action!
*Use command* `/groupid` and turnback her to enter *Admin Panel*""", reply_markup=kb.adder, parse_mode="Markdown")

@rtc.message(Command("help"))
async def help(message: types.Message):
    await message.answer(f"""*Aviable Commands:*
    */say* - Convert text to voice
    */groupid* - Show your group id
    */mystatus* - Show your status
    */gpt* - Chat with GPT-3

*Admin Commands:*     
    */filter* - enable or disable filter
    */kick* - Kick user
    */ban* - Ban user
    */mute* - Mute user
    """, parse_mode="Markdown")

@rtc.message(F.text == 'Connect to a Group⛓️‍💥')
async def fsm_trigger(message: types.Message, state: FSMContext):
    await state.set_state(Ser.group_id)
    prompt_message = await message.answer("Type chat id (without -): ", reply_markup=types.ReplyKeyboardRemove())
    await state.update_data(prompt_message_id=prompt_message.message_id)

@rtc.message(F.text == 'Social🧷')
async def fsm_trigger(message: types.Message, state: FSMContext):
    await message.answer_sticker('CAACAgIAAxkBAAIJFGcuO53MOKET0qamjv03PBy1A5GLAAJoAwACKvI6B3WVDI_oLIh3NgQ')
    await message.answer(f"Telegram moderation bot🦾.\nWrited in Python and developed by *hurkov*", parse_mode='Markdown', reply_markup=kb.social)


@rtc.message(Ser.group_id)
async def group_id_scan(message: types.Message, state: FSMContext):
    await state.update_data(group_id="-"+message.text)
    await state.update_data(user_id=message.from_user.id)
    data = await state.get_data()
    prompt_message_id = data.get("prompt_message_id")
    #if it works dont touch it
    if db.check_permissions(data["group_id"], data["user_id"]) is None:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=prompt_message_id)
        await message.delete()
        await message.answer(f"*Invalid group id⚠️*\nPlease try again..", parse_mode='Markdown', reply_markup=kb.main)
    elif db.check_permissions(data["group_id"], data["user_id"]):
        await message.bot.delete_message(chat_id=message.chat.id, message_id=prompt_message_id)
        await message.delete()
        await message.answer(f"""*Admin Panel*\n
*Bot🦾:* Access bot settings and features.
*Members📚:* Manage group members and their statuses.
*Tasker⛓:* Manage tasks by creating, viewing, and editing them.
*⚔Other:* Access miscellaneous options.""", reply_markup=kb.privilage, parse_mode="Markdown")
    elif not db.check_permissions(data["group_id"], data["user_id"]):
        await message.answer("Denied of permissions")


@rtc.callback_query(F.data == 'exit')
async def admp_exit(callback: types.CallbackQuery, state: FSMContext):
    global group_id
    await callback.message.delete()
    data = await state.get_data()
    group_id = data.get("group_id")
    await state.clear()
    await callback.message.answer_sticker('CAACAgIAAxkBAAIGTWcr3S5WEpVaYrTZCCPQWK-dtL7-AAJnAwACKvI6B9xHAeHmJ2-YNgQ')
    await callback.message.answer("See you next time!", reply_markup=kb.main)


@rtc.callback_query(F.data == "admp_bot")
async def admp_bot(callback: types.CallbackQuery):
    await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text="""*Bot Panel*\n
*Mailing📬:* Send messages to all group members.
*Ad Promo📰:* Create and manage promotional content.
*Back🔙:* Return to the previous menu.""",
        reply_markup=kb.admp_bot, parse_mode='Markdown')
    
@rtc.callback_query(F.data == "admp_mailing")
async def mailing(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer("Please send the content for the mailing (text, image with caption, or video with caption):")
    await state.set_state(Ser.mailing)

@rtc.message(Ser.mailing)
async def process_mailing(message: types.Message, state: FSMContext):
    if message.text:
        await state.update_data(mailing_type="text", mailing_content=message.text)
    elif message.photo:
        await state.update_data(mailing_type="image", mailing_content={"photo": message.photo[-1].file_id, "caption": message.caption})
    elif message.video:
        await state.update_data(mailing_type="video", mailing_content={"video": message.video.file_id, "caption": message.caption})
    else:
        await message.answer("Invalid content. Please try again.")
        return

    data = await state.get_data()
    mailing_type = data.get("mailing_type")
    mailing_content = data.get("mailing_content")
    group_id = data.get("group_id")

    if not group_id:
        await message.answer("Group ID is not set. Please set the group ID first.")
        return

    async def send_mailing():
        if mailing_type == "text":
            await message.bot.send_message(chat_id=group_id, text=mailing_content)
        elif mailing_type == "image":
            await message.bot.send_photo(chat_id=group_id, photo=mailing_content["photo"], caption=mailing_content["caption"])
        elif mailing_type == "video":
            await message.bot.send_video(chat_id=group_id, video=mailing_content["video"], caption=mailing_content["caption"])

    if promotion_task:
        global mailing_task
        mailing_task = asyncio.create_task(send_mailing())
    else:
        await send_mailing()

    await state.update_data(mailing_type=None, mailing_content=None)
    await message.answer_sticker('CAACAgIAAxkBAAIGYGcr3cR1HgmAKps7FvcxeXgpQkosAAJWAwACKvI6Bzbsis_jnYl7NgQ')
    await message.answer("Mailing sent.", reply_markup=kb.admp_bot)


@rtc.callback_query(F.data == "admp_promo")
async def admp_promo(callback: types.CallbackQuery, state: FSMContext):
    global promotion_task
    if promotion_task:
        await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text="Promotion is already running. Use the Stop button to stop it.",
        reply_markup=kb.stop_promo)
    else:
        await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text="Please select an option:",
        reply_markup=kb.promo_options)

@rtc.callback_query(F.data == "send_promo")
async def send_promo(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer("Please send the content for the promotion (text, image with caption, or video with caption):")
    await state.set_state(Ser.promo_content)

@rtc.message(Ser.promo_content)
async def process_promo_content(message: types.Message, state: FSMContext):
    if message.text:
        await state.update_data(promo_type="text", promo_content=message.text)
    elif message.photo:
        await state.update_data(promo_type="image", promo_content={"photo": message.photo[-1].file_id, "caption": message.caption})
    elif message.video:
        await state.update_data(promo_type="video", promo_content={"video": message.video.file_id, "caption": message.caption})
    else:
        await message.answer("Invalid content. Please try again.")
        return

    await message.answer("Please enter the interval in minuts for sending the promotion:")
    await state.set_state(Ser.promo_interval)

@rtc.message(Ser.promo_interval)
async def process_promo_interval(message: types.Message, state: FSMContext):
    try:
        interval = int(message.text)*60
        await state.update_data(promo_interval=interval)
    except ValueError:
        await message.answer("Invalid interval. Please enter the interval in minuts for sending the promotion:")
        return

    data = await state.get_data()
    promo_type = data.get("promo_type")
    promo_content = data.get("promo_content")
    promo_interval = data.get("promo_interval")
    group_id = data.get("group_id")

    await message.answer(f"Promotion scheduled every {promo_interval/60} minuts. Use the Stop button to stop.", reply_markup=kb.stop_promo)

    async def send_promo():
        while True:
            if promo_type == "text":
                await message.bot.send_message(chat_id=group_id, text=promo_content)
            elif promo_type == "image":
                await message.bot.send_photo(chat_id=group_id, photo=promo_content["photo"], caption=promo_content["caption"])
            elif promo_type == "video":
                await message.bot.send_video(chat_id=group_id, video=promo_content["video"], caption=promo_content["caption"])
            await asyncio.sleep(promo_interval)

    global promotion_task
    promotion_task = asyncio.create_task(send_promo())

@rtc.callback_query(F.data == "stop_promo")
async def stop_promo(callback: types.CallbackQuery):
    global promotion_task
    if promotion_task:
        promotion_task.cancel()
        promotion_task = None
        await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text="Promotion stopped.",
        reply_markup=kb.admp_bot)
    else:
        await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text="No active promotion to stop.",
        reply_markup=kb.promo_options)
    
@rtc.callback_query(F.data == "admp_members")
async def admp_members(callback: types.CallbackQuery):
    await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text="""*Members Panel*\n
*View Banned Users🗒️:* See the list of banned users.
*Unban User⚖️:* Remove a user from the banned list.
*Promote/Demote User📈:* Change a user's status between member and admin.
*View Member Infoℹ️:* Get detailed information about a member.""",
        reply_markup=kb.admp_members, parse_mode='Markdown')
    

@rtc.callback_query(F.data == "ban_list")
async def ban_list(callback: types.CallbackQuery, state: FSMContext):
    global group_id, banned_users, current_index
    data = await state.get_data()
    group_id = data.get("group_id")
    banned_users = db.ban(group_id)
    print(banned_users)
    current_index = 0
    if banned_users:
        await show_banned_user(callback)
    else:
        await callback.bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text="No banned users found.",
            reply_markup=kb.admp_bk_members)
        
@rtc.callback_query(F.data == "find_banned_member")
async def find_banned_member(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prompt_message = await callback.message.answer("Please enter the firstname or lastname of the banned member:")
    await state.update_data(prompt_message_id=prompt_message.message_id)
    await state.set_state(Ser.find_banned_member)

@rtc.message(Ser.find_banned_member)
async def process_find_banned_member(message: types.Message, state: FSMContext):
    global banned_users, current_index
    data = await state.get_data()
    prompt_message_id = data.get("prompt_message_id")

    if prompt_message_id:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=prompt_message_id)

    query = message.text.lower()
    found_users = [user for user in banned_users if (isinstance(user[1], str) and query in user[1].lower()) or (isinstance(user[2], str) and query in user[2].lower())]
    if found_users:
        # Set current_index to the index of the first found user
        current_index = banned_users.index(found_users[0])
        await show_banned_user(message)
    else:
        no_found = await message.answer("No banned members found with that name or username.\nWait! Returning to the list of banned members...")
        await message.delete()
        time.sleep(3)
        await no_found.delete()
        await show_banned_user(message)
    await state.update_data(prompt_message_id=None)

async def show_banned_user(event: types.CallbackQuery | types.Message):
    global current_index, banned_users
    user = banned_users[current_index]
    #text = f"Banned User {current_index + 1}/{len(banned_users)}:\n\n🏷️*User ID*: {user[1]}\n📎*Username*: {user[4]}\n🪪*Name*: {str(user[2])}\n⚖️*Status*: {user[7]}"
    text = f"Banned User {current_index + 1}/{len(banned_users)}:\n\n🏷️*User ID*: {user[1]}\n🪪*Name*: {str(user[2])}\n⚖️*Status*: {user[7]}"
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[], row_width=2)
    keyboard.inline_keyboard.append([types.InlineKeyboardButton(text="✅unban", callback_data="unban")])
    navigation_buttons = []
    if current_index > 0:
        navigation_buttons.append(types.InlineKeyboardButton(text="🔙Previous", callback_data="ban_prev"))
    if current_index < len(banned_users) - 1:
        navigation_buttons.append(types.InlineKeyboardButton(text="Next🔜", callback_data="ban_next"))
    if navigation_buttons:
        keyboard.inline_keyboard.append(navigation_buttons)
    keyboard.inline_keyboard.append([types.InlineKeyboardButton(text="Back🔙", callback_data="admp_members"), types.InlineKeyboardButton(text="Find🔍", callback_data="find_banned_member")])
    
    if isinstance(event, types.CallbackQuery):
        await event.bot.edit_message_text(
            chat_id=event.message.chat.id,
            message_id=event.message.message_id,
            text=text, parse_mode='MarkdownV2',
            reply_markup=keyboard)
    elif isinstance(event, types.Message):
        await event.answer(text, reply_markup=keyboard, parse_mode='MarkdownV2')

@rtc.callback_query(F.data == "unban")
async def ban_next(callback: types.CallbackQuery, state: FSMContext):
    global current_index, banned_users
    data = await state.get_data()
    group_id = data.get("group_id")
    await callback.message.bot.unban_chat_member(chat_id=group_id, user_id=banned_users[current_index][1])
    db.unban(group_id, banned_users[current_index][1])
    current_index += 1
    await show_banned_user(callback)

@rtc.callback_query(F.data == "ban_next")
async def ban_next(callback: types.CallbackQuery):
    global current_index
    current_index += 1
    await show_banned_user(callback)

@rtc.callback_query(F.data == "ban_prev")
async def ban_prev(callback: types.CallbackQuery):
    global current_index
    current_index -= 1
    await show_banned_user(callback)


@rtc.callback_query(F.data == "admp_back")
async def admp_back(callback: types.CallbackQuery):
    await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=f"""*Admin Panel*\n
*Bot🦾:* Access bot settings and features.
*Members📚:* Manage group members and their statuses.
*Tasker⛓:* Manage tasks by creating, viewing, and editing them.
*⚔Other:* Access miscellaneous options.""",
        reply_markup=kb.privilage, parse_mode='Markdown')
    
    
@rtc.callback_query(F.data == "boost_mem")
async def boost_member(callback: types.CallbackQuery):
    await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text="Boost Member:",
        reply_markup=kb.admp_booster)
    
@rtc.callback_query(F.data == "boost")
async def boost_member(callback: types.CallbackQuery, state: FSMContext):
    global status
    await state.update_data() 
    await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text="Mention User by Username:",
        reply_markup=None)
    status = callback.data
    await state.set_state(Ser.change_status)

@rtc.callback_query(F.data == "demote")
async def boost_member(callback: types.CallbackQuery, state: FSMContext):
    global status
    await state.update_data() 
    await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text="Mention User by Username:",
        reply_markup=None)
    status = callback.data
    await state.set_state(Ser.change_status)

@rtc.message(Ser.change_status)
async def booste_member(message: types.Message, state: FSMContext):
    change_status = message.text
    await state.update_data(change_status=change_status)
    data = await state.get_data()
    group_id = data.get("group_id")
    tag = data.get("change_status")
    global status
    if status == "demote":
        status = "member"
    elif status == "boost":
        status = "administrator"
    status_changed = db.status_changer(group_id, tag, status)
    if status_changed == True:
        await message.answer(f"User {tag} became {status}!", reply_markup=kb.admp_members)
    elif status_changed == False:   
        await message.answer(f"User {tag} is already {status}!", reply_markup=kb.admp_members)
    elif status_changed == None:
        await message.answer(f"User {tag} not found!", reply_markup=kb.admp_members)

@rtc.callback_query(F.data == 'admp_tasker')
async def admp_tasker(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    group_id = data.get("group_id")
    trello_data = db.trello_connect(group_id)
    print(trello_data)
    if trello_data == True:
        trello_status = "active✅"
    elif trello_data == False:
        trello_status = "inactive❌"
    await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=f"Manage your tasks with Trello or Notion.\n\n*Trello: {trello_status}*", parse_mode='Markdown',
        reply_markup=kb.admp_tasker)
    
@rtc.callback_query(F.data == 'bk_tasker')
async def bk_tasker(callback: types.CallbackQuery):
    await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=f"""*Admin Panel*\n
*Bot🦾:* Access bot settings and features.
*Members📚:* Manage group members and their statuses.
*Tasker⛓:* Manage tasks by creating, viewing, and editing them.
*⚔Other:* Access miscellaneous options.""",
        reply_markup=kb.privilage, parse_mode='Markdown')

@rtc.callback_query(F.data == 'trello')
async def bk_tasker(callback: types.CallbackQuery):
    await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=f"""*API Key:*

Go to the Trello Developer API Keys page.
Log in with your Trello account.
Your API key will be displayed on the page. Copy this key.

*Token:*

On the same page where you obtained your API key, there is a link to generate a token.
Click on the link *"Token"* or *"Generate a Token"*.
Authorize the application to access your Trello account.
Your token will be displayed. Copy this token.
Obtain Trello List ID:

*List ID:*
Go to your Trello board where you want to add tasks.
Export the board to JSON format and search for idList
*API & Token:* https://docs.adaptavist.com/w4j/latest/quick-configuration-guide/add-sources/how-to-generate-trello-api-key-token 
""",
        reply_markup=kb.trello, parse_mode='Markdown')
    
@rtc.callback_query(F.data == 'trello_disconnect')
async def tasker_trigger(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    group_id = data.get("group_id")
    db.trello_disconnect(group_id)
    await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=f"Trello API key and token have been disconnected.",
        reply_markup=kb.privilage, parse_mode='Markdown')

@rtc.callback_query(F.data == 'trello_connect')
async def tasker_trigger(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer("Please enter your Trello API key:")
    await state.set_state(Ser.api_key)

@rtc.message(Ser.api_key)
async def process_trello_api_key(message: types.Message, state: FSMContext):
    trello_api_key = message.text
    await state.update_data(api_key=trello_api_key)
    await message.delete()
    await message.answer("Please enter your Trello idList:")
    await state.set_state(Ser.board)

@rtc.message(Ser.board)
async def process_trello_api_key(message: types.Message, state: FSMContext):
    trello_board = message.text
    await state.update_data(board=trello_board)
    await message.delete()
    await message.answer("Please enter your Trello token:")
    await state.set_state(Ser.token)

@rtc.message(Ser.token)
async def process_trello_token(message: types.Message, state: FSMContext):
    trello_token = message.text
    await state.update_data(token=trello_token)
    await message.delete()
    data = await state.get_data()
    group_id = data.get("group_id")
    trello_api_key = data.get("api_key")
    trello_token = data.get("token")
    trello_board = data.get("board")
    db.trello(trello_token, trello_board, trello_api_key, group_id)
    trello_data = db.trello_connect(group_id)
    print(trello_data)
    if trello_data == True:
        trello_status = "active✅"
    elif trello_data == False:
        trello_status = "inactive❌"
    
    await message.answer(f"Manage your tasks with Trello or Notion.\n\n*Trello: {trello_status}*", parse_mode='Markdown', reply_markup=kb.admp_tasker)


@rtc.message(Command("todo"))
async def add_todo_task(message: types.Message, state: FSMContext):
    trello_data = db.trello_connect(message.chat.id)
    if trello_data == False:
        await message.answer("Please set your Trello API key and token using the Tasker button.")
        return

    task_text = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    if not task_text:
        await message.answer("Please provide a task description.")
        return

    trello_arr = db.trello_data(message.chat.id)
    token = trello_arr[0]
    board = trello_arr[1] 
    api_key = trello_arr[2] # Replace with your Trello list ID
    url = f"https://api.trello.com/1/cards"
    query = {
        'key': api_key,
        'token': token,
        'idList': board,
        'name': task_text
    }

    response = requests.post(url, params=query)
    if response.status_code == 200:
        await message.answer("Task added to Trello successfully!")
    else:
        await message.answer(f"Failed to add task to Trello. Error: {response.text}")
        await message.answer("Add:")
    await state.set_state(Ser.details)


@rtc.callback_query(F.data == 'db_export')
async def db_export(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    group_id = data.get("group_id")
    db.db_export(group_id)
    file_path = os.path.abspath('info.xlsx')
    await callback.message.answer_document(document=types.FSInputFile(path=file_path, filename=('info.xlsx')))

@rtc.message(Command("say"), F.text)
async def echo_voice(message: types.Message):
    _, text_to_voice = message.text.split('say', maxsplit=1)
    voice = gtts.tts.gTTS(text_to_voice, lang='it', tld='es')
    voice.save('voice.mp3')
    voice_file=types.FSInputFile("voice.mp3")
    await message.answer_voice(voice_file)


@rtc.message(Command("groupid"))
async def ustat(message: types.Message):
    chat_id = message.chat.id
    await message.answer(f"Your group id is {str(chat_id)[1:]}")


@rtc.message(Command("mystatus"))
async def ustat(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id  # The user issuing the command
    chat_member = await message.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    status = chat_member.status
    await message.answer(f"Your status is {status}")



@rtc.message(Command("gpt"))
async def gpt_neo(message: types.Message):
    client = Groq(api_key="GPT3_API_KEY")
    chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"{message.text}", 
                }
            ],
            model="llama3-8b-8192",
        )

    bad_bool = chat_completion.choices[0].message.content
    await message.answer(f"`{bad_bool}`")



@rtc.message(Command('filter'), F.text)
async def filter_status(message: types.Message):
    _, status = message.text.split('filter', maxsplit=1)
    status = status.lower()
    chat_member = await message.bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
    if status == None:
        mess = await message.reply("Please specify whether you want to enable or disable the filter.")
        time.sleep(5)
        await mess.delete()
        return
    if chat_member.status not in ['creator', 'administrator']:
        await message.reply("You cannot change filter status. You must be an admin.")
        return
    
    bd_status = await db.bd_status(message.chat.id)
    if "enable" in status and bd_status == False:
        await db.bd_status_change(status, message.chat.id)
        await message.answer("Chat filter was enabled!")
    elif "disable" in status and bd_status == True:
        await db.bd_status_change(status, message.chat.id)
        await message.answer("Chat filter was disabled!")
    else:
        await message.answer(f"filter is already{status}d")



@rtc.message(Command('kick'))
async def kick_user(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id  # The user issuing the command
    chat_member = await message.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    status = chat_member.status

    # Step 1: Check if the user issuing the /kick command is an admin
    if status not in ['creator', 'administrator']:
        await message.reply("You don't have permission to kick users. You must be an admin.")
        return

    # Step 2: Ensure the /kick command is in reply to a user's message
    # Extract the user mention
    if message.reply_to_message and message.reply_to_message.from_user:
        user_to_kick = message.reply_to_message.from_user
        user_id = user_to_kick.id
    elif message.entities:
        for entity in message.entities:
            if entity.type == "mention":
                username = message.text[entity.offset:entity.offset + entity.length]
                username = username[1:]
                print(username)
                try: 
                    user_id = await db.look_for_member(username)
                    user_to_kick = username
                except Exception as e:
                    await message.reply(f"An error occurred finding user: {e}")
    else:
        await message.reply("Please reply or mention user you want to kick.")
        return
    

    if user_to_kick is None:
        await message.reply("Please reply to a user's message to kick")
        return

    # Step 3: Get the user ID of the person to be kicked
    print(user_id)
    chat_member = await message.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    status = chat_member.status
    print(status)
    # Step 4: Check if the user to be kicked is also an admin (cannot kick admins)
    if status in ['creator', 'administrator']:
        await message.reply("You cannot kick an admin!")
        return

    try:
        # Step 5: Kick the user
        await message.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
        await message.reply(f"User {message.reply_to_message.from_user.full_name} has been kicked!")
        await message.bot.unban_chat_member(chat_id=chat_id, user_id=user_id,)
    except Exception as e:
        await message.reply(f"An error occurred: {e}")




@rtc.message(Command('ban'), F.text)
async def kick_user(message: types.Message):
    timecheck = True
    _, timer = message.text.split('ban', maxsplit=1)
    timer = timer.lower()
    if timer.startswith(" @"):
        timecheck = False
        time_type = None
    elif not timer:
        mess = await message.reply(f"The order of commands to ban: `/ban 'time' '@username`\nTimer:\n*sec* - seconds\n*min* - minut\n*h* - hour\n*mon* - month\nExample: `/ban 20sec @mark`", parse_mode="Markdown")
        time.sleep(5)
        await mess.delete()
        return
    if "sec" in timer and timecheck == True:
        timer = timer[:timer.index("sec") + len("sec")]
        timer = int(timer.replace("sec", ""))
        time_type ="sec"
    elif "min" in timer and timecheck == True:
        timer = timer[:timer.index("min") + len("min")]
        timer = int(timer.replace("min", ""))
        timer = timer * 60
        time_type ="min"
    elif "h" in timer and timecheck == True:
        timer = timer[:timer.index("h") + len("h")]
        timer = int(timer.replace("h", ""))
        timer = timer * 60 * 60
        time_type ="hour"
    elif "mon" in timer and timecheck == True:
        timer = timer[:timer.index("mon") + len("mon")]
        timer = int(timer.replace("mon", ""))
        timer = timer * 30 * 24 * 60 * 60 
        time_type ="mon"

    chat_id = message.chat.id
    user_id = message.from_user.id  # The user issuing the command
    chat_member = await message.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    status = chat_member.status


    # Step 1: Check if the user issuing the /kick command is an admin
    if status not in ['creator', 'administrator']:
        await message.reply("You don't have permission to ban users. You must be an admin.")
        return

    # Step 2: Ensure the /kick command is in reply to a user's message
    # Extract the user mention
    if message.reply_to_message and message.reply_to_message.from_user:
        user_to_kick = message.reply_to_message.from_user
        user_id = user_to_kick.id
    elif message.entities:
        for entity in message.entities:
            if entity.type == "mention":
                username = message.text[entity.offset:entity.offset + entity.length]
                username = username[1:]
                print(username + " banned")
                try: 
                    user_id = await db.look_for_member(username)
                    user_to_kick = username
                except Exception as e:
                    await message.reply(f"An error occurred finding user: {e}")
                
    else:
        await message.reply("Please reply to the user's message you want to ban.")
        return
    
    if user_to_kick is None:
        await message.reply("Please reply to a user's message to ban")
        return

    # Step 3: Get the user ID of the person to be kicked
    chat_member = await message.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    status = chat_member.status
    # Step 4: Check if the user to be kicked is also an admin (cannot kick admins)
    if status in ['creator', 'administrator']:
        await message.reply("You cannot ban an admin!")
        return

    try:
        # Step 5: Kick the user
        await message.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
        if timer.isdigit() == False:
            db.change_user_status(int(chat_id), int(user_id), "banned")
            await message.reply(f"User [{username}](https://t.me/@id{user_id}) has been banned forever!", parse_mode="Markdown")
        elif timer.isdigit() == True:
            await message.reply(f"User [{username}](https://t.me/@id{user_id}) has been banned for {timer} {time_type}!", parse_mode="Markdown")
        if timecheck == True:
            time.sleep(timer)
            await message.reply(f"User [{username}](https://t.me/@id{user_id}) has been unbanned!", parse_mode="Markdown")
            await message.bot.unban_chat_member(chat_id=chat_id, user_id=user_id,)
    except Exception as e:
        pass



@rtc.message(Command('mute'), F.text)
async def kick_user(message: types.Message):
    _, timer = message.text.split('mute', maxsplit=1)
    if timer.startswith(" @"):
        mess = await message.reply(f"The order of commands to mute: `/mute 'time' '@username`\nTimer:\n*sec* - seconds\n*min* - minut\n*h* - hour\n*mon* - month\nExapmle: `/mute 20sec @mark`", parse_mode="Markdown")
        time.sleep(5)
        await mess.delete()
        return
    elif not timer:
        mess = await message.reply(f"The order of commands to ban: `/mute 'time' '@username`\nTimer:\n*sec* - seconds\n*min* - minut\n*h* - hour\n*mon* - month\nExample: `/mute 20sec @mark`", parse_mode="Markdown")
        time.sleep(5)
        await mess.delete()
        return
    timecheck = True
    timer = timer.lower()
    if "sec" in timer:
        timer = timer[:timer.index("sec") + len("sec")]
        timer = int(timer.replace("sec", ""))
        time_type ="sec"
    elif "min" in timer:
        timer = timer[:timer.index("min") + len("min")]
        timer = int(timer.replace("min", ""))
        timer = timer * 60
        time_type ="min"
    elif "h" in timer:
        timer = timer[:timer.index("h") + len("h")]
        timer = int(timer.replace("h", ""))
        timer = timer * 60 * 60
        time_type ="hour"
    elif "mon" in timer:
        timer = timer[:timer.index("mon") + len("mon")]
        timer = int(timer.replace("mon", ""))
        timer = timer * 30 * 24 * 60 * 60 
        time_type ="mon"
    elif "ethernity" in timer:
        time_type = "ethernity"
        timecheck = False

    chat_id = message.chat.id
    user_id = message.from_user.id  # The user issuing the command
    chat_member = await message.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    status = chat_member.status

    # Step 1: Check if the user issuing the /kick command is an admin
    if status not in ['creator', 'administrator']:
        await message.reply("You don't have permission to mute users. You must be an admin.")
        return

    # Step 2: Ensure the /kick command is in reply to a user's message
    # Extract the user mention
    if message.reply_to_message and message.reply_to_message.from_user:
        user_to_kick = message.reply_to_message.from_user
        user_id = user_to_kick.id
    elif message.entities:
        for entity in message.entities:
            if entity.type == "mention":
                username = message.text[entity.offset:entity.offset + entity.length]
                username = username[1:]
                print(username)
                try: 
                    user_id = await db.look_for_member(username)
                    user_to_kick = username
                except Exception as e:
                    await message.reply(f"An error occurred finding user: {e}")
    else:
        await message.reply("Please reply to the user's message you want to mute.")
        return
    
    if user_to_kick is None:
        await message.reply("Please reply to a user's message to mute")
        return

    # Step 3: Get the user ID of the person to be kicked
    chat_member = await message.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    status = chat_member.status
    # Step 4: Check if the user to be kicked is also an admin (cannot kick admins)
    if status in ['creator', 'administrator']:
        await message.reply("You cannot mute an admin!")
        return

    try:
        # Step 5: Mute the user
        await message.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
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

        await message.reply(f"User [{username}](https://t.me/@id{user_id}) has been muted for {timer} {time_type}!", parse_mode="Markdown")
        if timecheck == True:
            await message.reply(f"User [{username}](https://t.me/@id{user_id}) has been unmuted!", parse_mode="Markdown")

        await message.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions={
                "can_send_messages": True,  # Disable sending messages
                "can_send_media_messages": True,  # Disable media sending
                "can_send_polls": True,  # Disable sending polls
                "can_send_other_messages": True,  # Disable other types of messages
                "can_add_web_page_previews": True,  # Disable adding web page previews
            }
        )
    except Exception as e:
        await message.reply(f"An error occurred: {e}")
