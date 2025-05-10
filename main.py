import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from dotenv import load_dotenv
from anime_utils import AnimeUtils

# Load environment
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')
OWNER_ID = int(os.getenv('OWNER_ID'))
SUPPORT_CHAT = os.getenv('SUPPORT_CHAT')

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Handlers

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        f"Welcome to AnimeBot! Use /new to browse latest anime, /search <name>, or ask me directly.\nSupport: {SUPPORT_CHAT}"    )

def new_list(update: Update, context: CallbackContext):
    page = int(context.args[0]) if context.args else 1
    anime_page = AnimeUtils.fetch_new(page)
    buttons = []
    for a in anime_page[:5]:  # show 5 per page
        buttons.append([InlineKeyboardButton(f"{a['released']} – {a['title']}", callback_data=f"info|{a['url']}|{page}")])
    # Next page button
    buttons.append([InlineKeyboardButton('Next ▶️', callback_data=f"new|{page+1}")])
    update.message.reply_text('Newest Anime:', reply_markup=InlineKeyboardMarkup(buttons))


def search(update: Update, context: CallbackContext):
    if not context.args:
        return update.message.reply_text('Usage: /search <anime name>')
    q = '+'.join(context.args)
    results = AnimeUtils.search_anime(q)
    if not results:
        return update.message.reply_text('No results found.')
    buttons = [[InlineKeyboardButton(r['title'], callback_data=f"info|{r['url']}|1")] for r in results[:5]]
    update.message.reply_text('Search results:', reply_markup=InlineKeyboardMarkup(buttons))


def broadcast(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return
    msg = ' '.join(context.args)
    context.bot.send_message(chat_id=SUPPORT_CHAT, text=f"📢 Broadcast:\n{msg}")
    update.message.reply_text('Broadcast sent.')


def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data.split('|')
    cmd = data[0]
    if cmd == 'new':
        page = int(data[1])
        anime_page = AnimeUtils.fetch_new(page)
        buttons = [[InlineKeyboardButton(f"{a['released']} – {a['title']}", callback_data=f"info|{a['url']}|{page}")] for a in anime_page[:5]]
        buttons.append([InlineKeyboardButton('Next ▶️', callback_data=f"new|{page+1}")])
        query.edit_message_text('Newest Anime:', reply_markup=InlineKeyboardMarkup(buttons))
    elif cmd == 'info':
        url, page = data[1], int(data[2])
        # fetch detail page for info
        details = AnimeUtils.fetch_new(page)  # for simplicity, reuse fetch_new until better caching
        # find matching
        anime = next((a for a in details if a['url'] == url), None)
        text = f"*{anime['title']}*\nType: {anime['type']}\nEpisodes: {anime['episodes']}\nRating: {anime['rating']}\nReleased: {anime['released']}"
        buttons = [[InlineKeyboardButton('Watch Episodes ▶️', callback_data=f"episodes|{url}")]]
        query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(buttons))
    elif cmd == 'episodes':
        url = data[1]
        eps = AnimeUtils.fetch_episodes(url)
        buttons = [[InlineKeyboardButton(ep['episode'], callback_data=f"stream|{ep['video_url']}")] for ep in eps[-10:]]
        buttons.append([InlineKeyboardButton('☑️ Back', callback_data=f"info|{url}|1")])
        query.edit_message_text('Select episode:', reply_markup=InlineKeyboardMarkup(buttons))
    elif cmd == 'stream':
        video = data[1]
        query.edit_message_text(f"Watch here: {video}")


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('new', new_list))
    dp.add_handler(CommandHandler('search', search))
    dp.add_handler(CommandHandler('broadcast', broadcast))
    dp.add_handler(CallbackQueryHandler(button_handler))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
