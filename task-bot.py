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
    keyboard = [
        [InlineKeyboardButton("Add Task", callback_data='addtask')],
        [InlineKeyboardButton("View Tasks", callback_data='viewtasks')],
        [InlineKeyboardButton("Remove Task", callback_data='removetask')],
        [InlineKeyboardButton("Task History", callback_data='history')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Hello! I am your task management bot.\n"
        "Use the buttons below to interact with me or type the commands directly.",
        reply_markup=reply_markup
    )

# Callback for inline buttons
async def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == 'addtask':
        await query.edit_message_text(text="Please provide the task name using /addtask <task_name>")
    elif query.data == 'viewtasks':
        await viewtasks(update.callback_query, context, is_callback=True)
    elif query.data == 'removetask':
        await query.edit_message_text(text="Please provide the task name using /removetask <task_name>")
    elif query.data == 'history':
        await history(update.callback_query, context, is_callback=True)

# Command /addtask
async def addtask(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    task_name = ' '.join(context.args)
    if task_name:
        if user_id not in user_tasks:
            user_tasks[user_id] = []
        user_tasks[user_id].append(task_name)
        await update.message.reply_text(f"Task '{task_name}' added successfully.")
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
        task_list = "\n".join(f"{idx + 1}. {task}" for idx, task in enumerate(tasks))
        if is_callback:
            await update.edit_message_text(f"Your pending tasks:\n{task_list}")
        else:
            await update.message.reply_text(f"Your pending tasks:\n{task_list}")
    else:
        if is_callback:
            await update.edit_message_text("You have no pending tasks.")
        else:
            await update.message.reply_text("You have no pending tasks.")

# Command /removetask
async def removetask(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    task_name = ' '.join(context.args)
    tasks = user_tasks.get(user_id, [])
    if task_name in tasks:
        tasks.remove(task_name)
        await update.message.reply_text(f"Task '{task_name}' removed.")
    else:
        await update.message.reply_text("Task not found. Please provide the correct task name using /removetask <task_name>")

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
    application.add_handler(CommandHandler("viewtasks", viewtasks))
    application.add_handler(CommandHandler("removetask", removetask))
    application.add_handler(CommandHandler("history", history))
    application.add_handler(CallbackQueryHandler(button_callback))

    application.run_polling()

if __name__ == '__main__':
    main()
