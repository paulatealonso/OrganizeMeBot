from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from database import add_task, get_tasks, update_task_status
from keyboards import get_main_menu_keyboard
from messages import WELCOME_MESSAGE

async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    keyboard = get_main_menu_keyboard(user_id)
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        WELCOME_MESSAGE,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

async def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == 'addtask':
        await query.edit_message_text(text=f"{WELCOME_MESSAGE}\n\nPlease provide the task name using /addtask <task_name>", disable_web_page_preview=True)
    elif query.data == 'viewtasks':
        await viewtasks(query, context, is_callback=True)
    elif query.data == 'back':
        await start_callback(query, context)
    elif query.data.startswith('complete_'):
        task_index = int(query.data.split('_')[1])
        await completetask(query, context, task_index)
    elif query.data.startswith('remove_'):
        task_index = int(query.data.split('_')[1])
        await removetask(query, context, task_index)
    elif query.data.startswith('restore_'):
        task_type, task_index = query.data.split('_')[1:]
        task_index = int(task_index)
        await restoretask(query, context, task_type, task_index)
    elif query.data == 'history':
        await taskhistory(query, context, is_callback=True)
    elif query.data == 'help':
        await help_command(query, context, is_callback=True)

async def start_callback(query, context):
    user_id = query.from_user.id
    keyboard = get_main_menu_keyboard(user_id)
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        WELCOME_MESSAGE,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

async def addtask(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    task_name = ' '.join(context.args)
    if task_name:
        add_task(user_id, task_name)
        await update.message.reply_text(f"✅ Task '{task_name}' added successfully.")
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Menu", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"{WELCOME_MESSAGE}\n\nTask added. What would you like to do next?",
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    else:
        await update.message.reply_text("Please provide the task name using /addtask <task_name>")

async def viewtasks(update: Update, context: CallbackContext, is_callback=False):
    user_id = update.message.from_user.id if not is_callback else update.from_user.id
    tasks = get_tasks(user_id, status="pending")
    if tasks:
        buttons = []
        for idx, (rowid, task) in enumerate(tasks):
            task_button = InlineKeyboardButton(f"{idx + 1}. {task}", callback_data=f"task_{rowid}")
            complete_button = InlineKeyboardButton("✅ Complete", callback_data=f"complete_{rowid}")
            remove_button = InlineKeyboardButton("❌ Remove", callback_data=f"remove_{rowid}")
            buttons.append([task_button])
            buttons.append([complete_button, remove_button])
        buttons.append([InlineKeyboardButton("🔙 Back to Menu", callback_data='back')])
        reply_markup = InlineKeyboardMarkup(buttons)
        message_text = "📝 Your pending tasks:"
        if is_callback:
            await update.edit_message_text(message_text, reply_markup=reply_markup, disable_web_page_preview=True)
        else:
            await update.message.reply_text(message_text, reply_markup=reply_markup, disable_web_page_preview=True)
    else:
        message_text = "You have no pending tasks."
        if is_callback:
            await update.edit_message_text(message_text, disable_web_page_preview=True)
        else:
            await update.message.reply_text(message_text, disable_web_page_preview=True)

async def completetask(update: Update, context: CallbackContext, task_index: int):
    user_id = update.from_user.id
    update_task_status(task_index, "completed")
    await update.edit_message_text(f"{WELCOME_MESSAGE}\n\n✅ Task marked as completed.", disable_web_page_preview=True)
    await start_callback(update, context)

async def removetask(update, context: CallbackContext, task_index: int):
    user_id = update.from_user.id
    update_task_status(task_index, "removed")
    await update.edit_message_text(f"{WELCOME_MESSAGE}\n\n❌ Task removed.", disable_web_page_preview=True)
    await start_callback(update, context)

async def restoretask(update, context: CallbackContext, task_type: str, task_index: int):
    user_id = update.from_user.id
    if task_type == 'completed':
        update_task_status(task_index, "pending")
        await update.edit_message_text(f"{WELCOME_MESSAGE}\n\n♻️ Task restored to pending.", disable_web_page_preview=True)
        await start_callback(update, context)
    elif task_type == 'removed':
        update_task_status(task_index, "pending")
        await update.edit_message_text(f"{WELCOME_MESSAGE}\n\n♻️ Task restored to pending.", disable_web_page_preview=True)
        await start_callback(update, context)

async def taskhistory(update, context: CallbackContext, is_callback=False):
    user_id = update.message.from_user.id if not is_callback else update.from_user.id
    comp_tasks = get_tasks(user_id, status="completed")
    rem_tasks = get_tasks(user_id, status="removed")
    if comp_tasks or rem_tasks:
        buttons = []
        if comp_tasks:
            for idx, (rowid, task) in enumerate(comp_tasks):
                buttons.append([InlineKeyboardButton(f"✅ {idx + 1}. {task}", callback_data=f"task_completed_{rowid}")])
                buttons.append([InlineKeyboardButton(f"♻️ Restore '{task}'", callback_data=f"restore_completed_{rowid}")])
        if rem_tasks:
            for idx, (rowid, task) in enumerate(rem_tasks):
                buttons.append([InlineKeyboardButton(f"❌ {idx + 1}. {task}", callback_data=f"task_removed_{rowid}")])
                buttons.append([InlineKeyboardButton(f"♻️ Restore '{task}'", callback_data=f"restore_removed_{rowid}")])
        buttons.append([InlineKeyboardButton("🔙 Back to Menu", callback_data='back')])
        reply_markup = InlineKeyboardMarkup(buttons)
        message_text = f"{WELCOME_MESSAGE}\n\n📜 Your task history:"
        if is_callback:
            await update.edit_message_text(message_text, reply_markup=reply_markup, disable_web_page_preview=True)
        else:
            await update.message.reply_text(message_text, reply_markup=reply_markup, disable_web_page_preview=True)
    else:
        message_text = "No task history available."
        if is_callback:
            await update.edit_message_text(message_text, disable_web_page_preview=True)
        else:
            await update.message.reply_text(message_text, disable_web_page_preview=True)

async def help_command(update, context: CallbackContext, is_callback=False):
    help_text = (
        "Help\n\n"
        "Here are the available commands:\n"
        "/start - Start the bot and show the main menu\n"
        "/addtask <task_name> - Add a new task\n"
        "/viewtasks - View your pending tasks\n"
        "/taskhistory - View the task history\n"
        "/help - Show this help message\n"
    )
    buttons = [[InlineKeyboardButton("🔙 Back to Menu", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(buttons)
    message_text = f"{WELCOME_MESSAGE}\n\n{help_text}"
    if is_callback:
        await update.edit_message_text(text=message_text, reply_markup=reply_markup, disable_web_page_preview=True)
    else:
        await update.message.reply_text(text=message_text, reply_markup=reply_markup, disable_web_page_preview=True)
