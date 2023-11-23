import logging
import os
import re
import shutil
from urllib.parse import urlparse

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (Application, CommandHandler, ContextTypes,
                          ConversationHandler, Job, MessageHandler, filters)

from scancrawl.core.app import App
from scancrawl.core.mongodb import MongoDBHandler
from scancrawl.model.TelegramUser import TelegramUser
from scancrawl.model.Scan import Scan

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self):
        # Initialize the MongoDB handler
        self.mongo_handler = MongoDBHandler()

    def start(self):
        os.environ["debug_mode"] = "yes"

        # Build the Application and with bot's token.
        TOKEN = os.getenv("TELEGRAM_TOKEN", "")
        self.application = Application.builder().token(TOKEN).build()

        # Add a command helper for help
        self.application.add_handler(CommandHandler("help", self.show_help))

        # Add a command helper for test
        self.application.add_handler(CommandHandler("teste", self.handle_teste))

        # Add conversation handler with states
        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler("start", self.init_app),
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND), self.handle_novel_url
                ),
            ],
            fallbacks=[
                CommandHandler("cancel", self.destroy_app),
            ],
            states={
                "handle_novel_url": [
                    MessageHandler(
                        filters.TEXT & ~(filters.COMMAND), self.handle_novel_url
                    ),
                ],
            },
        )
        self.application.add_handler(conv_handler)

        # Log all errors
        self.application.add_error_handler(self.error_handler)

        print("Telegram bot is online!")

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        # Start the Bot
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Log Errors caused by Updates."""
        logger.warn("Error: %s\nCaused by: %s", context.error, update)
    
    async def handle_teste(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Testado com sucesso")
        return ConversationHandler.END

    async def show_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Send /start to create new session.\n")
        return ConversationHandler.END

    def get_current_jobs(self, update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id=None):
        if update:
            name = str(update.effective_message.chat_id)
        else:
            name = chat_id
        current_jobs = context.job_queue.get_jobs_by_name(name)
        return current_jobs

    async def destroy_app(self, update: Update, context: ContextTypes.DEFAULT_TYPE, job: Job = None):
        if update:
            chat_id = str(update.effective_message.chat_id)
        else:
            chat_id = job.chat_id

        for job in self.get_current_jobs(update, context, chat_id):
            job.schedule_removal()

        if job or context.user_data.get("app"):
            app = job.data.pop("app", None) or context.user_data.pop("app")
            app.destroy()
            # remove output path
            # shutil.rmtree(app.output_path, ignore_errors=True)

        await context.bot.send_message(chat_id, text="Session closed", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    async def init_app(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Retrieve user data from MongoDB
        user_id = update.message.from_user.id
        user_data = self.mongo_handler.get_user_data(user_id)

        if not user_data:
            # User data does not exist, create a new user
            self.mongo_handler.create_user(
                user_id,
                update.message.from_user.username,
                update.message.from_user.first_name,
                update.message.from_user.last_name
            )

            # Optionally, perform additional initialization for the new user
            new_user = TelegramUser(
                user_id,
                update.message.from_user.username,
                update.message.from_user.first_name,
                update.message.from_user.last_name,
            )

            # Save the new user instance or perform any other necessary actions
            user_data = {"user_id": user_id, "app": new_user}
            self.mongo_handler.save_user_data(user_id, user_data)
        else:
            # User data exists, retrieve existing user instance
            new_user = user_data["app"]

        # Set the user instance in the context for further use
        context.user_data["app"] = new_user

        await update.message.reply_text("A new session is created.")
        await update.message.reply_text(
            "I recognize input of these categories:\n"
            "- A query to search your Scans.\n"
            "Enter whatever you want or send /cancel to stop."
        )
        return "handle_novel_url"

    async def handle_novel_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.get_current_jobs(update, context):
            app = context.user_data.get("app")
            await update.message.reply_text(
                "%s\n"
                "%d out of %d chapters has been downloaded.\n"
                "To terminate this session send /cancel."
                % (context.user_data.get("status"), app.progress, len(app.chapters))
            )
        else:
            if context.user_data.get("app"):
                app = context.user_data.get("app")
            else:
                app = App()
                app.initialize()
                context.user_data["app"] = app

            app.user_input = update.message.text.strip()

            try:
                app.prepare_search()
            except Exception:
                await update.message.reply_text(
                    "Sorry! I only recognize these sources:\n"
                    + "https://github.com/dipu-bd/lightnovel-crawler#supported-sources"
                )
                await update.message.reply_text(
                    "Enter something again or send /cancel to stop."
                )
                await update.message.reply_text(
                    "You can send the novelupdates link of the novel too.",
                )
                return "handle_novel_url"

            if app.crawler:
                await update.message.reply_text("Got your page link")
                return await self.get_novel_info(update, context)

            if len(app.user_input) < 5:
                await update.message.reply_text(
                    "Please enter a longer query text (at least 5 letters)."
                )
                return "handle_novel_url"

            await update.message.reply_text("Got your query text")
            return await self.show_crawlers_to_search(update, context)

    async def show_crawlers_to_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        app = context.user_data.get("app")

        buttons = []

        def make_button(i, url):
            return "%d - %s" % (i + 1, urlparse(url).hostname)

        for i in range(1, len(app.crawler_links) + 1, 2):
            buttons += [
                [
                    make_button(i - 1, app.crawler_links[i - 1]),
                    make_button(i, app.crawler_links[i])
                    if i < len(app.crawler_links)
                    else "",
                ]
            ]

        await update.message.reply_text(
            "Choose where to search for your novel, \n"
            "or send /skip to search everywhere.",
            reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True),
        )
        return "handle_crawler_to_search"

    async def handle_crawler_to_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        app = context.user_data.get("app")

        link = update.message.text
        if link:
            selected_crawlers = []
            if link.isdigit():
                selected_crawlers += [app.crawler_links[int(link) - 1]]
            else:
                selected_crawlers += [
                    x
                    for i, x in enumerate(app.crawler_links)
                    if "%d - %s" % (i + 1, urlparse(x).hostname) == link
                ]

            if len(selected_crawlers) != 0:
                app.crawler_links = selected_crawlers

        await update.message.reply_text(
            'Searching for "%s" in %d sites. Please wait.'
            % (app.user_input, len(app.crawler_links)),
            reply_markup=ReplyKeyboardRemove(),
        )
        await update.message.reply_text(
            "DO NOT type anything until I reply.\n"
            "You can only send /cancel to stop this session."
        )

        app.search_novel()
        return await self.show_novel_selection(update, context)

    async def show_novel_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        app = context.user_data.get("app")

        if len(app.search_results) == 0:
            await update.message.reply_text(
                "No results found by your query.\n" "Try again or send /cancel to stop."
            )
            return "handle_novel_url"

        if len(app.search_results) == 1:
            context.user_data["selected"] = app.search_results[0]
            return self.show_source_selection(update, context)

        await update.message.reply_text(
            "Choose any one of the following novels,"
            + " or send /cancel to stop this session.",
            reply_markup=ReplyKeyboardMarkup(
                [
                    [
                        "%d. %s (in %d sources)"
                        % (index + 1, res["title"], len(res["novels"]))
                    ]
                    for index, res in enumerate(app.search_results)
                ],
                one_time_keyboard=True,
            ),
        )

        return "handle_select_novel"

    async def handle_select_novel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        app = context.user_data.get("app")

        selected = None
        text = update.message.text
        if text:
            if text.isdigit():
                selected = app.search_results[int(text) - 1]
            else:
                for i, item in enumerate(app.search_results[:10]):
                    sample = "%d. %s" % (i + 1, item["title"])
                    if text.startswith(sample):
                        selected = item
                    elif len(text) >= 5 and text.lower() in item["title"].lower():
                        selected = item
                    else:
                        continue

                    break

        if not selected:
            return await self.show_novel_selection(update, context)

        context.user_data["selected"] = selected
        return await self.show_source_selection(update, context)

    async def show_source_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        app = context.user_data.get("app")
        selected = context.user_data.get("selected")
        assert isinstance(app, App)

        if len(selected["novels"]) == 1:
            app.crawler = prepare_crawler(selected["novels"][0]["url"])
            return await self.get_novel_info(update, context)

        await update.message.reply_text(
            ('Choose a source to download "%s", ' % selected["title"])
            + "or send /cancel to stop this session.",
            reply_markup=ReplyKeyboardMarkup(
                [
                    [
                        "%d. %s %s"
                        % (
                            index + 1,
                            novel["url"],
                            novel["info"] if "info" in novel else "",
                        )
                    ]
                    for index, novel in enumerate(selected["novels"])
                ],
                one_time_keyboard=True,
            ),
        )

        return "handle_select_source"

    async def handle_select_source(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        app = context.user_data.get("app")
        selected = context.user_data.get("selected")
        assert isinstance(app, App)

        source = None
        text = update.message.text
        if text:
            if text.isdigit():
                source = selected["novels"][int(text) - 1]
            else:
                for i, item in enumerate(selected["novels"]):
                    sample = "%d. %s" % (i + 1, item["url"])
                    if text.startswith(sample):
                        source = item
                    elif len(text) >= 5 and text.lower() in item["url"].lower():
                        source = item
                    else:
                        continue

                    break

        if not selected or not (source and source.get("url")):
            return await self.show_source_selection(update, context)

        app.crawler = prepare_crawler(source.get("url"))
        return await self.get_novel_info(update, context)

    async def get_novel_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        app = context.user_data.get("app")
        # user = update.message.from_user

        await update.message.reply_text(app.crawler.novel_url)

        # TODO: Implement login feature. Create login_info_dict of (email, password)
        # if app.can_do('login'):
        #     app.login_data = login_info_dict.get(app.crawler.home_url)
        #

        await update.message.reply_text("Reading novel info...")
        app.get_novel_info()

        if os.path.exists(app.output_path):
            await update.message.reply_text(
                "Local cache found do you want to use it",
                reply_markup=ReplyKeyboardMarkup(
                    [["Yes", "No"]], one_time_keyboard=True
                ),
            )
            return "handle_delete_cache"
        else:
            os.makedirs(app.output_path, exist_ok=True)
            # Get chapter range
            await update.message.reply_text(
                "%d volumes and %d chapters found."
                % (len(app.crawler.volumes), len(app.crawler.chapters)),
                reply_markup=ReplyKeyboardRemove(),
            )
            return await self.display_range_selection_help(update)

    async def handle_delete_cache(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        app = context.user_data.get("app")
        text = update.message.text
        if text.startswith("No"):
            if os.path.exists(app.output_path):
                shutil.rmtree(app.output_path, ignore_errors=True)
            os.makedirs(app.output_path, exist_ok=True)

        # Get chapter range
        await update.message.reply_text(
            "%d volumes and %d chapters found."
            % (len(app.crawler.volumes), len(app.crawler.chapters)),
            reply_markup=ReplyKeyboardRemove(),
        )
        return await self.display_range_selection_help(update)