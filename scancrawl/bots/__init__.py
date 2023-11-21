supported_bots = [
    "telegram",
]

def run_bot(bot):
    if bot not in supported_bots:
        bot = "telegram"

    if bot == "telegram":
        from ..bots.telegram import TelegramBot

        TelegramBot().start()
    else:
        print("Unknown bot: %s" % bot)