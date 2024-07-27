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
    "✨ How to Use the Bot:\n"
    "1. ➕ Add Task: Use the button or command /addtask <task_name> to add a new task.\n"
    "2. 📝 View Tasks: View your pending tasks.\n"
    "3. ✅ Complete Tasks: Mark a task as completed.\n"
    "4. ❌ Remove Tasks: Remove a task you no longer need.\n"
    "5. 📜 Task History: View your completed and removed tasks.\n\n"
    "🔗 Useful Links:\n"
    "🔹 Follow more of my projects on GitHub: https://github.com/paulatealonso\n"
    "🔹 Join our Reddit community: https://www.reddit.com/r/TONCALLSECURE/\n"
    "🔹 Check out our sponsored TON call channel: https://t.me/TONCALLSECURE\n\n"
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
async def viewtasks(update: Update, context: CallbackContext, is_callback=False):
    user_id = update.message.from_user.id if not is_callback else update.from_user.id
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

# Command /restoretask
async def restoretask(update, context: CallbackContext, task_type: str, task_index: int):
    user_id = update.from_user.id
    if task_type == 'completed':
        tasks = completed_tasks.get(user_id, [])
        if 0 <= task_index < len(tasks):
            task_name = tasks.pop(task_index)
            if user_id not in user_tasks:
                user_tasks[user_id] = []
            user_tasks[user_id].append(task_name)
            await update.edit_message_text(f"{WELCOME_MESSAGE}\n\n♻️ Task '{task_name}' restored to pending.", disable_web_page_preview=True)
            await start_callback(update, context)
        else:
            await update.message.reply_text("Task not found.")
    elif task_type == 'removed':
        tasks = removed_tasks.get(user_id, [])
        if 0 <= task_index < len(tasks):
            task_name = tasks.pop(task_index)
            if user_id not in user_tasks:
                user_tasks[user_id] = []
            user_tasks[user_id].append(task_name)
            await update.edit_message_text(f"{WELCOME_MESSAGE}\n\n♻️ Task '{task_name}' restored to pending.", disable_web_page_preview=True)
            await start_callback(update, context)
        else:
            await update.message.reply_text("Task not found.")

# Command /taskhistory
async def taskhistory(update, context: CallbackContext, is_callback=False):
    user_id = update.message.from_user.id if not is_callback else update.from_user.id
    comp_tasks = completed_tasks.get(user_id, [])
    rem_tasks = removed_tasks.get(user_id, [])
    if comp_tasks or rem_tasks:
        task_list = ""
        buttons = []
        if comp_tasks:
            task_list += "✅ Completed Tasks:\n" + "\n".join(f"{idx + 1}. {task}" for idx, task in enumerate(comp_tasks))
            for idx, task in enumerate(comp_tasks):
                buttons.append([InlineKeyboardButton(f"♻️ Restore '{task}'", callback_data=f"restore_completed_{idx}")])
        if rem_tasks:
            task_list += "\n\n❌ Removed Tasks:\n" + "\n".join(f"{idx + 1}. {task}" for idx, task in enumerate(rem_tasks))
            for idx, task in enumerate(rem_tasks):
                buttons.append([InlineKeyboardButton(f"♻️ Restore '{task}'", callback_data=f"restore_removed_{idx}")])
        buttons.append([InlineKeyboardButton("🔙 Back to Menu", callback_data='back')])
        reply_markup = InlineKeyboardMarkup(buttons)
        message_text = f"📜 Your task history:\n{task_list}"
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

# Command /help
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

def main():
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
