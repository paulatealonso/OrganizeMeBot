import os
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from dotenv import load_dotenv
from handlers import start, addtask, viewtasks, completetask, removetask, restoretask, taskhistory, help_command, button_callback
from database import init_db

# Load environment variables from .env file
load_dotenv()

# Get the token from the environment variable
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

# Verify that the environment variable is set
if TELEGRAM_API_TOKEN is None:
    raise ValueError("TELEGRAM_API_TOKEN not found in environment variables")

def main():
    # Initialize the database
    init_db()

    # Use the token obtained from the environment variable
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addtask", addtask))
    application.add_handler(CommandHandler("viewtasks", viewtasks))
    application.add_handler(CommandHandler("taskhistory", taskhistory))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))

    application.run_polling(stop_signals=None)

if __name__ == '__main__':
    main()
