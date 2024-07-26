import os
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the token from the environment variable
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

# Verify that the environment variable is set
if TELEGRAM_API_TOKEN is None:
    raise ValueError("TELEGRAM_API_TOKEN not found in environment variables")

# Command /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Hello! I am your task management bot.\n"
        "Use /addtask to add a task.\n"
        "Use /viewtasks to view your pending tasks.\n"
        "Use /completetask to mark a task as completed.\n"
        "Use /removetask to remove a task.\n"
        "Use /history to view the task history."
    )

# Command /addtask
async def addtask(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    task_name = ' '.join(context.args)
    if task_name:
        # Here you would add the logic to store the task in the database
        await update.message.reply_text(f"Task '{task_name}' added successfully.")
    else:
        await update.message.reply_text("Please provide the task name using /addtask <task_name>")

# Command /viewtasks
async def viewtasks(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    # Here you would add the logic to get tasks from the database
    tasks = "Here your pending tasks will appear."
    await update.message.reply_text(tasks)

# Command /completetask
async def completetask(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    task_name = ' '.join(context.args)
    if task_name:
        # Here you would add the logic to mark the task as completed
        await update.message.reply_text(f"Task '{task_name}' marked as completed.")
    else:
        await update.message.reply_text("Please provide the task name using /completetask <task_name>")

# Command /removetask
async def removetask(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    task_name = ' '.join(context.args)
    if task_name:
        # Here you would add the logic to remove the task
        await update.message.reply_text(f"Task '{task_name}' removed.")
    else:
        await update.message.reply_text("Please provide the task name using /removetask <task_name>")

# Command /history
async def history(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    # Here you would add the logic to get the task history from the database
    history = "Here your task history will appear."
    await update.message.reply_text(history)

def main():
    # Use the token obtained from the environment variable
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addtask", addtask))
    application.add_handler(CommandHandler("viewtasks", viewtasks))
    application.add_handler(CommandHandler("completetask", completetask))
    application.add_handler(CommandHandler("removetask", removetask))
    application.add_handler(CommandHandler("history", history))

    application.run_polling()

if __name__ == '__main__':
    main()
