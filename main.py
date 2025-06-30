from flask import Flask
import threading
import telebot
import requests
from telebot import types

TOKEN = "your_real_token_here"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route("/")
def health():
    return "OK", 200  # This must return quickly for Koyeb to pass health check

def run_bot():
    try:
        print("Starting bot polling...")
        bot.polling(non_stop=True)
    except Exception as e:
        print(f"Bot failed: {e}")

if __name__ == "__main__":
    print("Launching Flask and bot...")
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8080)

# Function to fetch token details from DexScreener
def fetch_token_data(contract_address):
    url = f"https://api.dexscreener.com/latest/dex/tokens/{contract_address}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data and isinstance(data, dict) and 'pairs' in data:
            pairs = data.get('pairs', [])
            if isinstance(pairs, list) and len(pairs) > 0:
                return pairs[0]  # Return first pair
        return None  # If no valid pairs found
    except requests.exceptions.RequestException:
        return None  # Handle network errors gracefully

# Function to fetch live SOL price from CoinGecko
def get_sol_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data and isinstance(data, dict) and "solana" in data and "usd" in data["solana"]:
            return float(data["solana"]["usd"])
        return None  # If the expected structure is missing
    except requests.exceptions.RequestException:
        return None

# Function to format large numbers into human-readable format
def format_large_number(value):
    if value >= 1_000_000_000:  # Billions
        return f"{value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:  # Millions
        return f"{value / 1_000_000:.2f}M"
    else:
        return f"{value:,.0f}"  # Normal number with commas

# Handle start command
@bot.message_handler(commands=['start'])
def start(message):
    # Step 1: Send the warning message and pin it
    warning_message = """
⚠️ WARNING: DO NOT CLICK on any ADs at the top of Telegram, they are NOT from us and most likely SCAMS.

Telegram now displays ADS in our bots without our approval. MP Rug Tool will NEVER advertise any links, airdrop claims, groups or discounts on fees.

For support, contact ONLY @mprugsupport, Support Staff and Admins will never Direct Message first or call you!
"""
    pinned_message = bot.send_message(message.chat.id, warning_message)
    bot.pin_chat_message(message.chat.id, pinned_message.message_id)

    # Step 2: Send the contract info and balance message
    markup = types.InlineKeyboardMarkup()

    markup.row(
        types.InlineKeyboardButton("Create Token 🛠️", callback_data="buy"),
        types.InlineKeyboardButton("My Tokens 🗂️", callback_data="sell")
    )
    markup.row(
        types.InlineKeyboardButton("Dump all 💣", callback_data="positions"),
        types.InlineKeyboardButton("Manual Dump 🧨", callback_data="limit_orders"),
        types.InlineKeyboardButton("Slow Dump 🐢", callback_data="dca_orders")
    )
    markup.row(
        types.InlineKeyboardButton("Generate Wallets ⚙️", callback_data="copy_trade"),
        types.InlineKeyboardButton("Distribute SOL 📤", callback_data="sniper")
    )
    markup.row(
        types.InlineKeyboardButton("Fake MC 📈", callback_data="trenches"),
        types.InlineKeyboardButton("Fake Liq 💧", callback_data="referrals"),
        types.InlineKeyboardButton("Fake Vol 📊", callback_data="watchlist")
    )
    markup.row(
        types.InlineKeyboardButton("Withdraw 🏦", callback_data="withdraw"),
        types.InlineKeyboardButton("Profits 💰", callback_data="settings")
    )
    markup.row(
        types.InlineKeyboardButton("Help", callback_data="help"),
        types.InlineKeyboardButton("↻ Refresh", callback_data="refresh")
    )

    # Send contract info and balance message
    bot.send_message(
        message.chat.id,
        "Solana · 🅴\n<code>6ZU2PV868iAt1wEq2LuexzDMmdYcWLgRzdTk6ASHSGLT</code>  <i>(Tap to copy)</i>\nBalance:<code> 0.00000000 SOL ($0.00) </code>\n—\nClick on the Refresh button to update your current balance.",
        parse_mode='HTML',
        reply_markup=markup
    )

# Handle button clicks
@bot.callback_query_handler(func=lambda call: True)
def handle_button_click(call):
    if call.data == "buy":
        bot.send_message(call.message.chat.id, "Not enought SOL")
    elif call.data == "sell":
        # Send the message with two buttons: Back and Refresh
        sell_message = bot.send_message(call.message.chat.id, "You do not have any tokens yet!! Create a token in the menu.")
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("← Back", callback_data="sell_back"),
            types.InlineKeyboardButton("↻ Refresh", callback_data="refresh")
        )
        bot.edit_message_reply_markup(call.message.chat.id, sell_message.message_id, reply_markup=markup)
    elif call.data == "sell_back":
        # Delete the message when 'Back' is clicked in the sell section
        bot.delete_message(call.message.chat.id, call.message.message_id)
    elif call.data == "positions":
        # Send position message with two buttons: Back and Refresh
        position_message = bot.send_message(call.message.chat.id, "You have no active token! Create a token in the menu.")
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("← Back", callback_data="sell_back"),  # Use the same "Back" as "sell"
            types.InlineKeyboardButton("↻ Refresh", callback_data="refresh")
        )
        bot.edit_message_reply_markup(call.message.chat.id, position_message.message_id, reply_markup=markup)
    elif call.data == "limit_orders":
        # Send limit orders message with two buttons: Back and Refresh
        limit_orders_message = bot.send_message(call.message.chat.id, "You have no active token! Create a token in the menu.")
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("← Back", callback_data="limit_orders_back"),
            types.InlineKeyboardButton("↻ Refresh", callback_data="refresh")
        )
        bot.edit_message_reply_markup(call.message.chat.id, limit_orders_message.message_id, reply_markup=markup)
    elif call.data == "limit_orders_back":
        # Delete the message when 'Back' is clicked in the Limit Orders section
        bot.delete_message(call.message.chat.id, call.message.message_id)
    elif call.data == "dca_orders":
        # Send DCA orders message with two buttons: Back and Refresh
        dca_orders_message = bot.send_message(call.message.chat.id, "You have no active token. Create a token in the menu.")
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("← Back", callback_data="dca_orders_back"),
            types.InlineKeyboardButton("↻ Refresh", callback_data="refresh")
        )
        bot.edit_message_reply_markup(call.message.chat.id, dca_orders_message.message_id, reply_markup=markup)
    elif call.data == "dca_orders_back":
        # Delete the message when 'Back' is clicked in the DCA Orders section
        bot.delete_message(call.message.chat.id, call.message.message_id)

    elif call.data == "copy_trade" or call.data == "sniper":
        # Send Copy Trade / Sniper message with two buttons: Back and Refresh
        message_text = (
            "<b>Create a token for this function to work</b>\n\n"

        )
        copy_trade_message = bot.send_message(
            call.message.chat.id, message_text, parse_mode="HTML"
        )

        # Add buttons for Back and Refresh
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("← Back", callback_data="copy_trade_back"),
            types.InlineKeyboardButton("↻ Refresh", callback_data="refresh")
        )
        bot.edit_message_reply_markup(call.message.chat.id, copy_trade_message.message_id, reply_markup=markup)

    elif call.data == "trenches":
        # Send Trenches message with two buttons: Back and Refresh
        message_text = (

            "Create a token for this function to work"
        )
        trenches_message = bot.send_message(
            call.message.chat.id, message_text, parse_mode="HTML"
        )

        # Add buttons for Back and Refresh
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("← Back", callback_data="trenches_back"),
            types.InlineKeyboardButton("↻ Refresh", callback_data="refresh")
        )
        bot.edit_message_reply_markup(call.message.chat.id, trenches_message.message_id, reply_markup=markup)

    elif call.data == "trenches_back":
        # Delete the message when 'Back' is clicked
        bot.delete_message(call.message.chat.id, call.message.message_id)

    elif call.data == "refresh":
        # Do nothing
        pass

    elif call.data == "copy_trade_back" or call.data == "sniper_back":
        # Delete the message when 'Back' is clicked
        bot.delete_message(call.message.chat.id, call.message.message_id)

    elif call.data == "refresh":
        # Do nothing
        pass

    elif call.data == "referrals":
        # Send Referrals message with two buttons: Back and Refresh
        message_text = (
            "Create a token for this function to work"
        )
        referrals_message = bot.send_message(
            call.message.chat.id, message_text, parse_mode="HTML"
        )

        # Add buttons for Back and Refresh
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("← Back", callback_data="referrals_back"),
            types.InlineKeyboardButton("↻ Refresh", callback_data="refresh")
        )
        bot.edit_message_reply_markup(call.message.chat.id, referrals_message.message_id, reply_markup=markup)

    elif call.data == "referrals_back":
        # Delete the message when 'Back' is clicked
        bot.delete_message(call.message.chat.id, call.message.message_id)

    elif call.data == "refresh":
        # Do nothing
        pass

    elif call.data == "watchlist":
        # Send Watchlist message with two buttons: Back and Refresh
        message_text = (
            "Create a token for this function to work"

        )
        watchlist_message = bot.send_message(
            call.message.chat.id, message_text, parse_mode="HTML"
        )

        # Add buttons for Back and Refresh
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("← Back", callback_data="watchlist_back"),
            types.InlineKeyboardButton("↻ Refresh", callback_data="refresh")
        )
        bot.edit_message_reply_markup(call.message.chat.id, watchlist_message.message_id, reply_markup=markup)

    elif call.data == "watchlist_back":
        # Delete the message when 'Back' is clicked
        bot.delete_message(call.message.chat.id, call.message.message_id)

    elif call.data == "refresh":
        # Do nothing
        pass

    elif call.data == "withdraw":
        # Send Withdraw message with two buttons: Back and Refresh
        message_text = (
           "<b>Withdraw $SOL — (Solana) 🅴</b>\n\n"
           "<b>Balance:</b> 0.00000000 SOL ($0.00)"
        )
        withdraw_message = bot.send_message(
            call.message.chat.id, message_text, parse_mode="HTML"
        )

    # Add buttons for Back and Refresh
        markup = types.InlineKeyboardMarkup()
        markup.row(
             types.InlineKeyboardButton("← Back", callback_data="withdraw_back"),
             types.InlineKeyboardButton("↻ Refresh", callback_data="refresh")
        )
        bot.edit_message_reply_markup(call.message.chat.id, withdraw_message.message_id, reply_markup=markup)

    elif call.data == "withdraw_back":
        # Delete the message when 'Back' is clicked
        bot.delete_message(call.message.chat.id, call.message.message_id)

    elif call.data == "settings":
        # Send Settings message with two buttons: Back and Refresh
        bot.send_message(
        call.message.chat.id,

           "No profits yet",
        parse_mode="HTML",
        reply_markup=types.InlineKeyboardMarkup().row(
            types.InlineKeyboardButton("← Back", callback_data="settings_back"),
            types.InlineKeyboardButton("↻ Refresh", callback_data="refresh")
        )
        )
    elif call.data == "settings_back":
        # Delete the message when 'Back' is clicked
        bot.delete_message(call.message.chat.id, call.message.message_id)

    elif call.data == "help":
        # Send Help message with two buttons: Back and Refresh (with ↻ icon)
        bot.send_message(
        call.message.chat.id,

        "Join our Telegram group @mprugtoolsol and one of our admins can assist you.",
        parse_mode="HTML",
        reply_markup=types.InlineKeyboardMarkup().row(
            types.InlineKeyboardButton("← Back", callback_data="help_back"),
            types.InlineKeyboardButton("↻ Refresh", callback_data="refresh")  # Added ↻ icon
        )
        )

    elif call.data == "help_back":
        # Delete the message when 'Back' is clicked
        bot.delete_message(call.message.chat.id, call.message.message_id)



    elif call.data == "back":
        # Send contract info and balance message again with buttons (without the warning message)
        markup = types.InlineKeyboardMarkup()

        markup.row(
            types.InlineKeyboardButton("Buy", callback_data="buy"),
            types.InlineKeyboardButton("Sell", callback_data="sell")
        )
        markup.row(
            types.InlineKeyboardButton("Positions", callback_data="positions"),
            types.InlineKeyboardButton("Limit Orders", callback_data="limit_orders"),
            types.InlineKeyboardButton("DCA Orders", callback_data="dca_orders")
        )
        markup.row(
            types.InlineKeyboardButton("Copy Trade", callback_data="copy_trade"),
            types.InlineKeyboardButton("Sniper 🆕", callback_data="sniper")
        )
        markup.row(
            types.InlineKeyboardButton("Trenches", callback_data="trenches"),
            types.InlineKeyboardButton("💰 Referrals", callback_data="referrals"),
            types.InlineKeyboardButton("⭐ Watchlist", callback_data="watchlist")
        )
        markup.row(
            types.InlineKeyboardButton("Withdraw", callback_data="withdraw"),
            types.InlineKeyboardButton("Settings", callback_data="settings")
        )
        markup.row(
            types.InlineKeyboardButton("Help", callback_data="help"),
            types.InlineKeyboardButton("↻ Refresh", callback_data="refresh")
        )

        # Send contract info and balance message again without the warning message
        bot.send_message(
            call.message.chat.id,
            "Solana · 🅴\n<code>6ZU2PV868iAt1wEq2LuexzDMmdYcWLgRzdTk6ASHSGLT</code>  <i>(Tap to copy)</i>\nBalance:<code> 0.00000000 SOL ($0.00) </code>\n—\nClick on the Refresh button to update your current balance.",
            parse_mode='HTML',
            reply_markup=markup
        )
    elif call.data == "refresh":
        # Do nothing — just return without sending any new message
        pass
    elif call.data == "positions":
        # Send position message with two buttons: Back and Refresh
        position_message = bot.send_message(call.message.chat.id, "You do not have any tokens yet! Start trading in the Buy menu.")
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("← Back", callback_data="sell_back"),  # Use the same "Back" as "sell"
            types.InlineKeyboardButton("↻ Refresh", callback_data="refresh")
        )
        bot.edit_message_reply_markup(call.message.chat.id, position_message.message_id, reply_markup=markup)

    elif call.data == "back":
        # Send contract info and balance message again with buttons (without the warning message)
        markup = types.InlineKeyboardMarkup()

        markup.row(
            types.InlineKeyboardButton("Buy", callback_data="buy"),
            types.InlineKeyboardButton("Sell", callback_data="sell")
        )
        markup.row(
            types.InlineKeyboardButton("Positions", callback_data="positions"),
            types.InlineKeyboardButton("Limit Orders", callback_data="limit_orders"),
            types.InlineKeyboardButton("DCA Orders", callback_data="dca_orders")
        )
        markup.row(
            types.InlineKeyboardButton("Copy Trade", callback_data="copy_trade"),
            types.InlineKeyboardButton("Sniper 🆕", callback_data="sniper")
        )
        markup.row(
            types.InlineKeyboardButton("Trenches", callback_data="trenches"),
            types.InlineKeyboardButton("💰 Referrals", callback_data="referrals"),
            types.InlineKeyboardButton("⭐ Watchlist", callback_data="watchlist")
        )
        markup.row(
            types.InlineKeyboardButton("Withdraw", callback_data="withdraw"),
            types.InlineKeyboardButton("Settings", callback_data="settings")
        )
        markup.row(
            types.InlineKeyboardButton("Help", callback_data="help"),
            types.InlineKeyboardButton("↻ Refresh", callback_data="refresh")
        )

        # Send contract info and balance message again without the warning message
        bot.send_message(
            call.message.chat.id,
            "Solana · 🅴\n<code>6ZU2PV868iAt1wEq2LuexzDMmdYcWLgRzdTk6ASHSGLT</code>  <i>(Tap to copy)</i>\nBalance:<code> 0.00000000 SOL ($0.00) </code>\n—\nClick on the Refresh button to update your current balance.",
            parse_mode='HTML',
            reply_markup=markup
        )
    elif call.data == "refresh":
        # Do nothing — just return without sending any new message
        pass
    elif call.data == "positions":
        # Send position message with two buttons: Back and Refresh
        position_message = bot.send_message(call.message.chat.id, "You do not have any tokens yet! Start trading in the Buy menu.")
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("← Back", callback_data="sell_back"),  # Use the same "Back" as "sell"
            types.InlineKeyboardButton("↻ Refresh", callback_data="refresh")
        )
        bot.edit_message_reply_markup(call.message.chat.id, position_message.message_id, reply_markup=markup)
# Handle user input (contract address)
@bot.message_handler(func=lambda message: True)
def handle_contract_input(message):
    contract_address = message.text.strip()
    token = fetch_token_data(contract_address)

    if token:
        name = token.get('baseToken', {}).get('name', 'Unknown')
        symbol = token.get('baseToken', {}).get('symbol', 'Unknown')
        price = float(token.get('priceUsd', 0)) if token.get('priceUsd') else 0

        liquidity = token.get('liquidity', {}).get('usd', 0) if token.get('liquidity') else 0
        market_cap = token.get('fdv', 0) if token.get('fdv') else 0

        # Format numbers safely
        liquidity_formatted = format_large_number(liquidity) if liquidity else "N/A"
        market_cap_formatted = format_large_number(market_cap) if market_cap else "N/A"

        sol_price = get_sol_price() or 113.24  # Use fallback price if API fails

        sol_amount = 0.5
        token_amount = (sol_amount * sol_price / price) if price > 0 else "N/A"

        message_text = f"""
*Buy ${symbol} — ({name}) 📈 • *
`{contract_address}`

**Balance:** *0 SOL*  
**Price:** `${price}`  
**LIQ:** `${liquidity_formatted}`  
**MC:** `${market_cap_formatted}`  
**Renounced** ✅    

**{sol_amount} SOL** → `{token_amount}` *{symbol}* (*${sol_amount * sol_price}*)  
**Price Impact:** `0.01%`

🔴 *Insufficient balance for buy amount + gas*
"""
        # Create buttons: Back and Refresh
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("← Back", callback_data="back"),
            types.InlineKeyboardButton("↻ Refresh", callback_data="refresh")
        )

        # Send the contract details with "Back" and "Refresh" buttons
        bot.send_message(message.chat.id, message_text, parse_mode="Markdown", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "❌ Invalid.")

