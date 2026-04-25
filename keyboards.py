from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config

def join_channel_keyboard():
    buttons = [
        [InlineKeyboardButton(text="📢 Join Channel", url=f"https://t.me/{Config.SUPPORT_USERNAME}")],
        [InlineKeyboardButton(text="✅ Check Membership", callback_data="check_membership")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def main_menu_keyboard():
    buttons = [
        [InlineKeyboardButton(text="🛒 Shop", callback_data="shop"),
         InlineKeyboardButton(text="🤑 Deposit", callback_data="deposit")],
        [InlineKeyboardButton(text="👤 My Profile", callback_data="profile"),
         InlineKeyboardButton(text="🆘 Support", callback_data="support")],
        [InlineKeyboardButton(text="⭐️ Refer & Earn", callback_data="referral")],
        [InlineKeyboardButton(text="👨‍💼 Admin Panel", callback_data="admin_panel")] if Config.ADMIN_ID else []
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def product_list_keyboard(products):
    buttons = []
    for product in products:
        buttons.append([InlineKeyboardButton(
            text=f"📦 {product['name']} - ₹{product['price']}",
            callback_data=f"product:{product['_id']}"
        )])
    buttons.append([InlineKeyboardButton(text="🔙 Back", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def quantity_keyboard():
    buttons = [
        [InlineKeyboardButton(text="1", callback_data="qty:1"),
         InlineKeyboardButton(text="2", callback_data="qty:2"),
         InlineKeyboardButton(text="3", callback_data="qty:3")],
        [InlineKeyboardButton(text="4", callback_data="qty:4"),
         InlineKeyboardButton(text="5", callback_data="qty:5"),
         InlineKeyboardButton(text="10", callback_data="qty:10")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_shop")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def payment_method_keyboard():
    buttons = [
        [InlineKeyboardButton(text="💰 Wallet", callback_data="payment:wallet")],
        [InlineKeyboardButton(text="💳 UPI Payment", callback_data="payment:upi")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_shop")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def upi_payment_keyboard():
    buttons = [
        [InlineKeyboardButton(text="💳 Pay Now", url=f"upi://pay?pa={Config.UPI_ID}&pn=Store&am=0")],
        [InlineKeyboardButton(text="✅ Paid", callback_data="paid")],
        [InlineKeyboardButton(text="🔙 Cancel", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def deposit_keyboard():
    buttons = [
        [InlineKeyboardButton(text="💳 Make Deposit", callback_data="make_deposit")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def profile_keyboard():
    buttons = [
        [InlineKeyboardButton(text="💰 Deposit", callback_data="deposit"),
         InlineKeyboardButton(text="📋 Order History", callback_data="order_history")],
        [InlineKeyboardButton(text="⭐️ Referral Info", callback_data="referral")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def referral_keyboard(link):
    buttons = [
        [InlineKeyboardButton(text="💰 Transfer to Wallet", callback_data="transfer_earnings")],
        [InlineKeyboardButton(text="💸 Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton(text="📤 Share Link", url=f"https://t.me/share/url?url={link}&text=Join this awesome bot!")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_profile")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def support_keyboard():
    buttons = [
        [InlineKeyboardButton(text="📩 Contact Support", url=f"https://t.me/{Config.SUPPORT_USERNAME}")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def back_to_main_keyboard():
    buttons = [[InlineKeyboardButton(text="🔙 Back to Main Menu", callback_data="back_to_main")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def back_to_profile_keyboard():
    buttons = [[InlineKeyboardButton(text="🔙 Back to Profile", callback_data="back_to_profile")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def admin_main_keyboard():
    buttons = [
        [InlineKeyboardButton(text="📦 Products", callback_data="admin_products"),
         InlineKeyboardButton(text="💳 Payments", callback_data="admin_payments")],
        [InlineKeyboardButton(text="💰 Deposits", callback_data="admin_deposits"),
         InlineKeyboardButton(text="💸 Withdraws", callback_data="admin_withdraws")],
        [InlineKeyboardButton(text="📋 Orders", callback_data="admin_orders"),
         InlineKeyboardButton(text="👥 Users", callback_data="admin_users")],
        [InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast"),
         InlineKeyboardButton(text="📊 Earnings", callback_data="admin_earnings")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def admin_products_keyboard(products):
    buttons = []
    for product in products[:5]:  # Show first 5 products
        buttons.append([InlineKeyboardButton(
            text=f"✏️ {product['name']}",
            callback_data=f"edit_product:{product['_id']}"
        )])
    buttons.append([InlineKeyboardButton(text="➕ Add Product", callback_data="add_product")])
    buttons.append([InlineKeyboardButton(text="🔙 Back", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def admin_edit_product_keyboard():
    buttons = [
        [InlineKeyboardButton(text="✏️ Edit Name", callback_data="edit_name"),
         InlineKeyboardButton(text="💰 Edit Price", callback_data="edit_price")],
        [InlineKeyboardButton(text="📝 Edit Description", callback_data="edit_description"),
         InlineKeyboardButton(text="📦 Add Stock", callback_data="add_stock")],
        [InlineKeyboardButton(text="🗑 Delete Product", callback_data="delete_product")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="admin_products")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def admin_approve_keyboard(type):
    buttons = [
        [InlineKeyboardButton(text="✅ Approve", callback_data=f"approve_{type}"),
         InlineKeyboardButton(text="❌ Reject", callback_data=f"reject_{type}")],
        [InlineKeyboardButton(text="🔙 Back", callback_data=f"admin_{type}s")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def cancel_keyboard():
    buttons = [[InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def skip_keyboard():
    buttons = [
        [InlineKeyboardButton(text="⏭ Skip for now", callback_data="skip_stock")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def admin_back_keyboard():
    buttons = [[InlineKeyboardButton(text="🔙 Back to Admin Panel", callback_data="admin_panel")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
