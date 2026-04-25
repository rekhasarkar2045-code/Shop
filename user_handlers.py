from aiogram import types, Dispatcher, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import *
from utils import generate_referral_link, format_currency
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class OrderState(StatesGroup):
    selecting_product = State()
    entering_quantity = State()
    payment_method = State()
    uploading_screenshot = State()
    entering_utr = State()

class WithdrawState(StatesGroup):
    entering_amount = State()
    entering_upi = State()

async def start_command(message: types.Message, db, bot):
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    
    if not user:
        # Check for referral
        args = message.text.split()
        referrer_id = int(args[1]) if len(args) > 1 and args[1].isdigit() else None
        await db.create_user(user_id, message.from_user.username, message.from_user.first_name, referrer_id)
    
    # Check channel membership (mock - implement actual check)
    await message.answer(
        "📢 *Please join our channel to continue*\n\n"
        "Click the button below to join and then click 'Check ✅'",
        reply_markup=join_channel_keyboard(),
        parse_mode="Markdown"
    )

async def check_membership(callback: types.CallbackQuery, db, bot):
    # Implement actual channel check here
    await callback.message.edit_text(
        "✅ *Welcome to the E-commerce Bot!*\n\n"
        "Your one-stop shop for digital products.\n"
        "Use the buttons below to navigate:",
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

async def shop_menu(callback: types.CallbackQuery, db, bot):
    products = await db.get_products()
    if not products:
        await callback.message.edit_text(
            "📦 *No products available*\n\n"
            "Check back later for new products!",
            reply_markup=back_to_main_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text(
            "🛒 *Our Products*\n\n"
            "Select a product to view details:",
            reply_markup=product_list_keyboard(products),
            parse_mode="Markdown"
        )
    await callback.answer()

async def product_details(callback: types.CallbackQuery, db, bot, state: FSMContext):
    product_id = callback.data.split(":")[1]
    product = await db.get_product(product_id)
    
    if product:
        await state.update_data(product_id=product_id, product_name=product["name"], 
                               product_price=product["price"])
        text = f"📦 *{product['name']}*\n\n"
        text += f"💰 *Price:* ₹{product['price']}\n"
        text += f"📝 *Description:* {product['description']}\n"
        text += f"📊 *Stock:* {len(product.get('stock', []))} units\n\n"
        text += "How many units would you like to buy?"
        
        await callback.message.edit_text(
            text,
            reply_markup=quantity_keyboard(),
            parse_mode="Markdown"
        )
        await state.set_state(OrderState.entering_quantity)
    await callback.answer()

async def process_quantity(callback: types.CallbackQuery, db, bot, state: FSMContext):
    if callback.data == "back_to_shop":
        await shop_menu(callback, db, bot)
        await state.clear()
        return
    
    quantity = int(callback.data.split(":")[1])
    data = await state.get_data()
    total = data["product_price"] * quantity
    
    await state.update_data(quantity=quantity, total=total)
    
    text = f"🛒 *Order Summary*\n\n"
    text += f"📦 Product: {data['product_name']}\n"
    text += f"🔢 Quantity: {quantity}\n"
    text += f"💰 Price/unit: ₹{data['product_price']}\n"
    text += f"💵 *Total: ₹{total}*\n\n"
    text += "Select payment method:"
    
    await callback.message.edit_text(
        text,
        reply_markup=payment_method_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(OrderState.payment_method)
    await callback.answer()

async def process_payment_method(callback: types.CallbackQuery, db, bot, state: FSMContext):
    method = callback.data.split(":")[1]
    data = await state.get_data()
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    if method == "wallet":
        if user["wallet"] >= data["total"]:
            # Process wallet payment
            await db.update_wallet(user_id, -data["total"])
            order_id = await db.create_order(
                user_id, data["product_id"], data["quantity"], 
                data["total"], "wallet"
            )
            
            # Get delivery code
            code = await db.get_stock_code(data["product_id"])
            if code:
                await db.complete_order(order_id, code)
                await callback.message.edit_text(
                    f"✅ *Payment Successful!*\n\n"
                    f"Your product code: `{code}`\n\n"
                    f"Order ID: {order_id}\n"
                    f"Amount deducted: ₹{data['total']}\n"
                    f"Remaining balance: ₹{user['wallet'] - data['total']}",
                    reply_markup=main_menu_keyboard(),
                    parse_mode="Markdown"
                )
            else:
                await callback.message.edit_text(
                    "❌ *Out of Stock!*\n\n"
                    "Product is no longer available. Your money has been refunded.",
                    reply_markup=main_menu_keyboard(),
                    parse_mode="Markdown"
                )
                await db.update_wallet(user_id, data["total"])
        else:
            await callback.message.edit_text(
                f"❌ *Insufficient Balance!*\n\n"
                f"Your balance: ₹{user['wallet']}\n"
                f"Required: ₹{data['total']}\n"
                f"Need more: ₹{data['total'] - user['wallet']}\n\n"
                f"Please deposit funds to continue.",
                reply_markup=deposit_keyboard(),
                parse_mode="Markdown"
            )
    
    elif method == "upi":
        await callback.message.edit_text(
            f"💳 *UPI Payment*\n\n"
            f"Send ₹{data['total']} to:\n"
            f"`{Config.UPI_ID}`\n\n"
            f"After payment, click 'Paid ✅' below and upload screenshot with UTR number.",
            reply_markup=upi_payment_keyboard(),
            parse_mode="Markdown"
        )
        await state.set_state(OrderState.uploading_screenshot)
    
    await callback.answer()

async def deposit_menu(callback: types.CallbackQuery, db, bot):
    await callback.message.edit_text(
        f"💰 *Deposit Money*\n\n"
        f"Send amount to:\n`{Config.UPI_ID}`\n\n"
        f"After payment, send:\n"
        f"1. Screenshot of payment\n"
        f"2. UTR number\n\n"
        f"*Minimum deposit: ₹100*\n"
        f"*Maximum deposit: ₹50,000*",
        reply_markup=deposit_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

async def profile_menu(callback: types.CallbackQuery, db, bot):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    
    text = f"👤 *Your Profile*\n\n"
    text += f"🆔 ID: `{user_id}`\n"
    text += f"💰 Wallet: ₹{user['wallet']}\n"
    text += f"📅 Joined: {user['joined_at'].strftime('%Y-%m-%d')}\n"
    text += f"👥 Referrals: {len(user.get('referrals', []))}\n"
    text += f"⭐️ Referral Earnings: ₹{user.get('referral_earnings', 0)}"
    
    await callback.message.edit_text(
        text,
        reply_markup=profile_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

async def referral_info(callback: types.CallbackQuery, db, bot):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    link = generate_referral_link(user_id)
    
    text = f"⭐️ *Referral Program*\n\n"
    text += f"Earn {Config.REFERRAL_PERCENT}% commission on every purchase!\n"
    text += f"Plus ₹{Config.REFERRAL_BONUS} bonus when your referral makes first purchase!\n\n"
    text += f"📊 *Your Stats:*\n"
    text += f"👥 Total Referrals: {len(user.get('referrals', []))}\n"
    text += f"💰 Total Earned: ₹{user.get('total_earned', 0)}\n"
    text += f"💵 Available: ₹{user.get('referral_earnings', 0)}\n\n"
    text += f"🔗 *Your Referral Link:*\n`{link}`"
    
    await callback.message.edit_text(
        text,
        reply_markup=referral_keyboard(link),
        parse_mode="Markdown"
    )
    await callback.answer()

async def order_history(callback: types.CallbackQuery, db, bot):
    user_id = callback.from_user.id
    orders = await db.get_user_orders(user_id)
    
    if not orders:
        text = "📋 *No orders found*"
    else:
        text = "📋 *Your Order History*\n\n"
        for order in orders:
            product = await db.get_product(order["product_id"])
            text += f"🆔 {order['order_id']}\n"
            text += f"📦 {product['name'] if product else 'Unknown'} x{order['quantity']}\n"
            text += f"💰 ₹{order['total_price']}\n"
            text += f"⏰ {order['created_at'].strftime('%Y-%m-%d %H:%M')}\n"
            text += f"📊 {order['status'].upper()}\n"
            text += "─" * 20 + "\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=back_to_profile_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

async def support_menu(callback: types.CallbackQuery, db, bot):
    await callback.message.edit_text(
        f"🆘 *Support Center*\n\n"
        f"For any issues or queries, please contact our support team.\n\n"
        f"Response time: Usually within 24 hours\n\n"
        f"Click the button below to message support:",
        reply_markup=support_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

def register_user_handlers(dp: Dispatcher, db, bot):
    dp.message.register(lambda m: start_command(m, db, bot), Command("start"))
    dp.callback_query.register(lambda c: check_membership(c, db, bot), F.data == "check_membership")
    dp.callback_query.register(lambda c: shop_menu(c, db, bot), F.data == "shop")
    dp.callback_query.register(lambda c: deposit_menu(c, db, bot), F.data == "deposit")
    dp.callback_query.register(lambda c: profile_menu(c, db, bot), F.data == "profile")
    dp.callback_query.register(lambda c: support_menu(c, db, bot), F.data == "support")
    dp.callback_query.register(lambda c: referral_info(c, db, bot), F.data == "referral")
    dp.callback_query.register(lambda c: order_history(c, db, bot), F.data == "order_history")
    dp.callback_query.register(lambda c: product_details(c, db, bot, None), F.data.startswith("product:"))
    dp.callback_query.register(lambda c: process_quantity(c, db, bot, None), F.data.startswith("qty:"))
    dp.callback_query.register(lambda c: process_payment_method(c, db, bot, None), F.data.startswith("payment:"))
