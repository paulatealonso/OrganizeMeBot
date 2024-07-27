import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the token from the environment variable
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

# Verify that the environment variable is set
if TELEGRAM_API_TOKEN is None:
    raise ValueError("TELEGRAM_API_TOKEN not found in environment variables")

# Dictionary to store tasks per user
user_tasks = {}
completed_tasks = {}
removed_tasks = {}

# Welcome and Description Message
WELCOME_MESSAGE = (
    "👋 Welcome to the Task Management Bot!\n"
    "I am here to help you manage your tasks efficiently.\n\n"
    "🔹 Use the buttons below to interact with me or type the commands directly.\n"
    "🔹 Check out our sponsored TON call channel: [TON Call Secure](https://t.me/TONCALLSECURE)\n\n"
    "Feel free to reach out if you have any questions or need assistance."
)

# Function to generate the main menu keyboard
def get_main_menu_keyboard(user_id):
    if user_id in user_tasks and user_tasks[user_id]:
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

# Command /start
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    keyboard = get_main_menu_keyboard(user_id)
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        WELCOME_MESSAGE,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

# Callback for inline buttons
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
    elif query.data == 'history':
        await history(query, context, is_callback=True)
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

# Command /addtask
async def addtask(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    task_name = ' '.join(context.args)
    if task_name:
        if user_id not in user_tasks:
            user_tasks[user_id] = []
        user_tasks[user_id].append(task_name)
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

# Command /viewtasks
async def viewtasks(update, context: CallbackContext, is_callback=False):
    if is_callback:
        user_id = update.from_user.id
    else:
        user_id = update.message.from_user.id
    tasks = user_tasks.get(user_id, [])
    if tasks:
        buttons = []
        for idx, task in enumerate(tasks):
            buttons.append([InlineKeyboardButton(f"{idx + 1}. {task}", callback_data=f"task_{idx}")])
            buttons.append([
                InlineKeyboardButton("✅ Complete", callback_data=f"complete_{idx}"),
                InlineKeyboardButton("❌ Remove", callback_data=f"remove_{idx}")
            ])
        buttons.append([InlineKeyboardButton("🔙 Back to Menu", callback_data='back')])
        reply_markup = InlineKeyboardMarkup(buttons)
        if is_callback:
            await update.edit_message_text(f"{WELCOME_MESSAGE}\n\n📝 Your pending tasks:", reply_markup=reply_markup, disable_web_page_preview=True)
        else:
            await update.message.reply_text(f"{WELCOME_MESSAGE}\n\n📝 Your pending tasks:", reply_markup=reply_markup, disable_web_page_preview=True)
    else:
        if is_callback:
            await update.edit_message_text(f"{WELCOME_MESSAGE}\n\nYou have no pending tasks.", disable_web_page_preview=True)
        else:
            await update.message.reply_text(f"{WELCOME_MESSAGE}\n\nYou have no pending tasks.", disable_web_page_preview=True)

# Command /completetask
async def completetask(update: Update, context: CallbackContext, task_index: int):
    user_id = update.from_user.id
    tasks = user_tasks.get(user_id, [])
    if 0 <= task_index < len(tasks):
        task_name = tasks.pop(task_index)
        if user_id not in completed_tasks:
            completed_tasks[user_id] = []
        completed_tasks[user_id].append(task_name)
        await update.edit_message_text(f"{WELCOME_MESSAGE}\n\n✅ Task '{task_name}' marked as completed.", disable_web_page_preview=True)
        await start_callback(update, context)
    else:
        await update.message.reply_text("Task not found.")

# Command /removetask
async def removetask(update, context: CallbackContext, task_index: int):
    user_id = update.from_user.id
    tasks = user_tasks.get(user_id, [])
    if 0 <= task_index < len(tasks):
        task_name = tasks.pop(task_index)
        if user_id not in removed_tasks:
            removed_tasks[user_id] = []
        removed_tasks[user_id].append(task_name)
        await update.edit_message_text(f"{WELCOME_MESSAGE}\n\n❌ Task '{task_name}' removed.", disable_web_page_preview=True)
        await start_callback(update, context)
    else:
        await update.message.reply_text("Task not found.")

# Command /history
async def history(update, context: CallbackContext, is_callback=False):
    if is_callback:
        user_id = update.from_user.id
    else:
        user_id = update.message.from_user.id
    comp_tasks = completed_tasks.get(user_id, [])
    rem_tasks = removed_tasks.get(user_id, [])
    if comp_tasks or rem_tasks:
        task_list = ""
        if comp_tasks:
            task_list += "\n✅ Completed Tasks:\n" + "\n".join(f"{idx + 1}. {task}" for idx, task in enumerate(comp_tasks))
        if rem_tasks:
            task_list += "\n❌ Removed Tasks:\n" + "\n".join(f"{idx + 1}. {task}" for idx, task in enumerate(rem_tasks))
        buttons = [[InlineKeyboardButton("🔙 Back to Menu", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(buttons)
        if is_callback:
            await update.edit_message_text(f"{WELCOME_MESSAGE}\n\n📜 Your task history:\n{task_list}", reply_markup=reply_markup, disable_web_page_preview=True)
        else:
            await update.message.reply_text(f"{WELCOME_MESSAGE}\n\n📜 Your task history:\n{task_list}", reply_markup=reply_markup, disable_web_page_preview=True)
    else:
        if is_callback:
            await update.edit_message_text(f"{WELCOME_MESSAGE}\n\nNo task history available.", disable_web_page_preview=True)
        else:
            await update.message.reply_text(f"{WELCOME_MESSAGE}\n\nNo task history available.", disable_web_page_preview=True)

# Command /help
async def help_command(update, context: CallbackContext, is_callback=False):
    help_text = (
        "Help\n\n"
        "Here are the available commands:\n"
        "/start - Start the bot and show the main menu\n"
        "/addtask <task_name> - Add a new task\n"
        "/viewtasks - View your pending tasks\n"
        "/completetask <task_name> - Mark a task as completed\n"
        "/removetask <task_name> - Remove a task\n"
        "/history - View the task history\n"
    )
    buttons = [[InlineKeyboardButton("🔙 Back to Menu", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(buttons)
    if is_callback:
        await update.edit_message_text(text=f"{WELCOME_MESSAGE}\n\n{help_text}", reply_markup=reply_markup, disable_web_page_preview=True)
    else:
        await update.message.reply_text(text=f"{WELCOME_MESSAGE}\n\n{help_text}", reply_markup=reply_markup, disable_web_page_preview=True)

def main():
    # Use the token obtained from the environment variable
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addtask", addtask))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))

    application.run_polling(stop_signals=None)

if __name__ == '__main__':
    main()
