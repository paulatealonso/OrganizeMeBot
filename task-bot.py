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

# Command /start
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    keyboard = get_main_menu_keyboard(user_id)
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Hello! I am your task management bot.\n"
        "Use the buttons below to interact with me or type the commands directly.",
        reply_markup=reply_markup
    )

def get_main_menu_keyboard(user_id):
    if user_id in user_tasks and user_tasks[user_id]:
        return [
            [InlineKeyboardButton("Add Task", callback_data='addtask')],
            [InlineKeyboardButton("View Tasks", callback_data='viewtasks')],
            [InlineKeyboardButton("Task History", callback_data='history')]
        ]
    else:
        return [
            [InlineKeyboardButton("Add Task", callback_data='addtask')]
        ]

# Callback for inline buttons
async def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == 'addtask':
        await query.edit_message_text(text="Please provide the task name using /addtask <task_name>")
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

async def start_callback(query, context):
    user_id = query.from_user.id
    keyboard = get_main_menu_keyboard(user_id)
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "Hello! I am your task management bot.\n"
        "Use the buttons below to interact with me or type the commands directly.",
        reply_markup=reply_markup
    )

# Command /addtask
async def addtask(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    task_name = ' '.join(context.args)
    if task_name:
        if user_id not in user_tasks:
            user_tasks[user_id] = []
        user_tasks[user_id].append(task_name)
        await update.message.reply_text(f"Task '{task_name}' added successfully.")
        
        keyboard = [
            [InlineKeyboardButton("Back to Menu", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Task added. What would you like to do next?",
            reply_markup=reply_markup
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
        task_list = "\n".join(
            f"{idx + 1}. {task}\n"
            f"[Complete](callback_data=f'complete_{idx}') | [Remove](callback_data=f'remove_{idx}')"
            for idx, task in enumerate(tasks)
        )
        if is_callback:
            await update.edit_message_text(f"Your pending tasks:\n{task_list}")
        else:
            await update.message.reply_text(f"Your pending tasks:\n{task_list}")
    else:
        if is_callback:
            await update.edit_message_text("You have no pending tasks.")
        else:
            await update.message.reply_text("You have no pending tasks.")

# Command /completetask
async def completetask(update: Update, context: CallbackContext, task_index: int):
    user_id = update.from_user.id
    tasks = user_tasks.get(user_id, [])
    if 0 <= task_index < len(tasks):
        task_name = tasks.pop(task_index)
        await update.edit_message_text(f"Task '{task_name}' marked as completed.")
        await start_callback(update, context)
    else:
        await update.message.reply_text("Task not found.")

# Command /removetask
async def removetask(update, context: CallbackContext, task_index: int):
    user_id = update.from_user.id
    tasks = user_tasks.get(user_id, [])
    if 0 <= task_index < len(tasks):
        task_name = tasks.pop(task_index)
        await update.edit_message_text(f"Task '{task_name}' removed.")
        await start_callback(update, context)
    else:
        await update.message.reply_text("Task not found.")

# Command /history
async def history(update, context: CallbackContext, is_callback=False):
    if is_callback:
        user_id = update.from_user.id
    else:
        user_id = update.message.from_user.id
    tasks = user_tasks.get(user_id, [])
    if tasks:
        task_list = "\n".join(f"{idx + 1}. {task}" for idx, task in enumerate(tasks))
        if is_callback:
            await update.edit_message_text(f"Your task history:\n{task_list}")
        else:
            await update.message.reply_text(f"Your task history:\n{task_list}")
    else:
        if is_callback:
            await update.edit_message_text("No task history available.")
        else:
            await update.message.reply_text("No task history available.")

def main():
    # Use the token obtained from the environment variable
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addtask", addtask))
    application.add_handler(CallbackQueryHandler(button_callback))

    application.run_polling(stop_signals=None)

if __name__ == '__main__':
    main()
