from telegram import InlineKeyboardButton
from database import get_tasks

def get_main_menu_keyboard(user_id):
    tasks = get_tasks(user_id, status="pending")
    if tasks:
        return [
            [InlineKeyboardButton("➕ Add Task", callback_data='addtask')],
            [InlineKeyboardButton("📝 View Tasks", callback_data='viewtasks')],
            [InlineKeyboardButton("📜 Task History", callback_data='history')],
            [InlineKeyboardButton("ℹ️ Help", callback_data='help')]
        ]
    else:
        return [
            [InlineKeyboardButton("➕ Add Task", callback_data='addtask')],
            [InlineKeyboardButton("ℹ️ Help", callback_data='help')]
        ]
