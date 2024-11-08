import sqlite3 as sq
from openpyxl import Workbook


db = sq.connect('info.db')
cur = db.cursor()

async def db_start(): 
    cur.execute("CREATE TABLE IF NOT EXISTS group_info("
                "chat_id INTEGER PRIMARY KEY, "
                "group_title TEXT NOT NULL, "
                "chat_type TEXT NOT NULL, "
                "chat_username TEXT, "
                "chat_lang TEXT, "
                "trello_api TEXT, "
                "trello_token TEXT, "
                "trello_board TEXT, "
                "filter_status INTEGER DEFAULT 0 "
                ")")
    cur.execute("CREATE TABLE IF NOT EXISTS group_member_info("
                "group_id INTEGER, "
                "user_id INTEGER, "
                "user_first_name TEXT, "
                "user_last_name TEXT, "
                "user_username TEXT, "
                "user_premium BOOLEAN, "
                "user_is_bot BOOLEAN, "
                "user_status TEXT, "
                "bd_counter INTEGER DEFAULT 0, "
                "karma INTEGER "
                ")")
    db.commit()

async def group_join(chat_id, group_title, chat_type, chat_username):
    cur.execute('SELECT * FROM group_info WHERE chat_id = ?', (chat_id,))
    if cur.fetchone() is None:
        cur.execute('''
            INSERT INTO group_info (chat_id, group_title, chat_username, chat_type)
            VALUES (?, ?, ?, ?)
        ''', (chat_id, group_title, chat_username, chat_type))
        db.commit()

def new_member(chat_id, user_id, full_name, last_name, username, is_premium, is_bot, status):
    cur.execute('SELECT * FROM group_member_info WHERE user_id = ? AND group_id = ?', (user_id, chat_id))
    exist = cur.fetchone()
    if exist is None:
        cur.execute('''
            INSERT INTO group_member_info (group_id, user_id, user_first_name, user_last_name, user_username, user_premium, user_is_bot, user_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (chat_id, user_id, full_name, last_name, username, is_premium, is_bot, status))
    else:
        exist_id = exist[0]
        if exist_id != chat_id:
            cur.execute('''
                INSERT INTO group_member_info (group_id, user_id, user_first_name, user_last_name, user_username, user_premium, user_is_bot, user_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (chat_id, user_id, full_name, last_name, username, is_premium, is_bot, status))
    db.commit()


async def look_for_member(user_username):
    cur.execute("SELECT user_id FROM group_member_info WHERE user_username = ?", (user_username,))
    user_id = cur.fetchone()
    return user_id[0]

async def bd_status(chat_id):
    cur.execute("SELECT filter_status FROM group_info WHERE chat_id = ?", (chat_id,))
    bd_status = cur.fetchone()[0]
    if bd_status == 0:
        return False
    elif bd_status == 1:
        return True

async def bd_status_change(status, chat_id):
    if "enable" in status:
        status = 1
        cur.execute("UPDATE group_info SET filter_status = ? WHERE chat_id = ?", (status, chat_id,))
        db.commit()
    elif "disable" in status:
        status = 0
        cur.execute("UPDATE group_info SET filter_status = ? WHERE chat_id = ?", (status, chat_id,))
        db.commit()
    else:
        return None

async def bd_allert(user_id):
    cur.execute("UPDATE group_member_info SET bd_counter = bd_counter + 1 WHERE user_id = ?", (user_id,))
    db.commit()
    cur.execute("SELECT bd_counter FROM group_member_info WHERE user_id = ?", (user_id,))
    bd_check = cur.fetchone()[0]
    return bd_check
    

def check_lang(group_id):
    cur.execute("SELECT chat_lang FROM group_info WHERE chat_id = ?", (group_id,))
    lang_value = cur.fetchone()
    if lang_value and (lang_value[0] is None or lang_value[0] == ''):
        return True
    else:
        return False
    

def check_and_update_group_lang(group_id, detected_lang):
    # Check if the group_lang column is empty for the given group_id
    cur.execute("SELECT chat_lang FROM group_info WHERE chat_id = ?", (group_id,))
    lang_value = cur.fetchone()

    if lang_value and (lang_value[0] is None or lang_value[0] == ''):
        # If group_lang is empty or NULL, update it with the detected language
        cur.execute("UPDATE group_info SET chat_lang = ? WHERE chat_id = ?", (detected_lang, group_id))
        db.commit()
        result = "Group language detected and updated"
    else:
        result = "Group language is already set or group not found"
    return result

def ban(group_id):
    cur.execute("SELECT * FROM group_member_info WHERE group_id = ? AND user_status = ?", (group_id, 'banned',))
    user_status = cur.fetchall()
    return user_status

def unban(group_id, user_id):
    cur.execute("DELETE FROM group_member_info WHERE group_id = ? AND user_id = ?", (group_id, user_id))
    db.commit()

def change_user_status(chat_id, user_id, new_status):
    cur.execute("UPDATE group_member_info SET user_status = ? WHERE group_id = ? AND user_id = ?", (new_status, chat_id, user_id))
    db.commit()

def check_permissions(chat_id, user_id):
    cur.execute("SELECT EXISTS (SELECT user_status FROM group_member_info WHERE group_id = ? AND user_id = ?)", (chat_id, user_id))
    exists = cur.fetchone()[0]
    if exists:
        cur.execute("SELECT user_status FROM group_member_info WHERE group_id = ? AND user_id = ?", (chat_id, user_id))
        if cur.fetchone()[0] in ['creator', 'administrator']:
            return True
        else:
            return False
    elif not exists:
        return None
    
def db_export(chat_id):
    cur.execute("SELECT * FROM group_member_info WHERE group_id = ?", (chat_id,))
    rows = cur.fetchall()
    columns = [description[0] for description in cur.description]
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = 'members_get_info'
    sheet.append(columns)
    for row in rows:
        sheet.append(row)

# Save the workbook as an Excel file
    workbook.save('info.xlsx')
    print("Successfully exported")

def status_changer(chat_id, tag, new_status):
    # Use LIKE operator to check if the tag is contained within user_first_name or user_username
    cur.execute("SELECT user_status FROM group_member_info WHERE group_id = ? AND user_username = ?", (chat_id, tag,))
    status = cur.fetchone()
    if status:
        if status[0] == new_status:
            print("Status is already the same")
            return False 
            # Status is already the same
        else:
            cur.execute("UPDATE group_member_info SET user_status = ? WHERE group_id = ? AND (user_first_name LIKE ? OR user_username LIKE ?)", (new_status, chat_id, f"%{tag}%", f"%{tag}%"))
            db.commit()
            print("Status updated")
            return True  # Status updated
    else:
        print("No such user")
        return None  # No matching user found

def trello(trello_token, trello_board, trello_api, group_id):
    cur.execute("UPDATE group_info SET trello_token = ?, trello_board = ?, trello_api = ? WHERE chat_id = ?", (trello_token, trello_board, trello_api, group_id,))
    db.commit()

def trello_connect(group_id):
    cur.execute("SELECT trello_token, trello_board, trello_api FROM group_info WHERE chat_id = ?", (group_id,))
    trello_data = cur.fetchone()
    if trello_data and all(trello_data):  # Check if all elements in trello_data are not None or empty
        return True
    else:
        return False
    
def trello_disconnect(group_id):
    cur.execute("UPDATE group_info SET trello_token = NULL, trello_board = NULL, trello_api = NULL WHERE chat_id = ?", (group_id,))
    db.commit()

def trello_data(group_id):
    cur.execute("SELECT trello_token, trello_board, trello_api FROM group_info WHERE chat_id = ?", (group_id,))
    trello_data = cur.fetchone()
    return trello_data

