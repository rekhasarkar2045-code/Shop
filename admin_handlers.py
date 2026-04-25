from aiogram import types, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import *
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

class AdminProductState(StatesGroup):
    waiting_name = State()
    waiting_price = State()
    waiting_description = State()
    waiting_stock = State()
    waiting_product_id = State()

class AdminBroadcastState(StatesGroup):
    waiting_message = State()

async def admin_panel(callback: types.CallbackQuery, db, bot):
    if callback.from_user.id != Config.ADMIN_ID:
        await callback.answer("⛔️ Unauthorized!", show_alert=True)
        return
    
    stats = await db.get_stats()
    text = f"👨‍💼 *Admin Panel*\n\n"
    text += f"📊 *Statistics*\n"
    text += f"👥 Total Users: {stats['total_users']}\n"
    text += f"📦 Total Orders: {stats['total_orders']}\n"
    text += f"💰 Total Revenue: ₹{stats['total_revenue']}\n"
    text += f"📈 Today's Income: ₹{stats['today_income']}\n\n"
    text += f"Select an option below:"
    
    await callback.message.edit_text(
        text,
        reply_markup=admin_main_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

async def admin_products_menu(callback: types.CallbackQuery, db, bot):
    if callback.from_user.id != Config.ADMIN_ID:
        await callback.answer("⛔️ Unauthorized!", show_alert=True)
        return
    
    products = await db.get_products(active_only=False)
    await callback.message.edit_text(
        "📦 *Product Management*\n\n"
        "Select an option:",
        reply_markup=admin_products_keyboard(products),
        parse_mode="Markdown"
    )
    await callback.answer()

async def add_product_start(callback: types.CallbackQuery, db, bot, state: FSMContext):
    if callback.from_user.id != Config.ADMIN_ID:
        await callback.answer("⛔️ Unauthorized!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "➕ *Add New Product*\n\n"
        "Send me the product name:",
        reply_markup=cancel_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(AdminProductState.waiting_name)
    await callback.answer()

async def process_product_name(message: types.Message, db, bot, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        "💰 Send me the product price (in rupees):\n\n"
        "Example: 499",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(AdminProductState.waiting_price)

async def process_product_price(message: types.Message, db, bot, state: FSMContext):
    try:
        price = float(message.text)
        await state.update_data(price=price)
        await message.answer(
            "📝 Send me the product description:",
            reply_markup=cancel_keyboard()
        )
        await state.set_state(AdminProductState.waiting_description)
    except:
        await message.answer("❌ Invalid price! Please send a number.")

async def process_product_description(message: types.Message, db, bot, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(
        "📦 Send me the stock codes (one per line):\n\n"
        "Example:\n"
        "CODE123\n"
        "CODE456\n"
        "CODE789",
        reply_markup=skip_keyboard()
    )
    await state.set_state(AdminProductState.waiting_stock)

async def process_product_stock(message: types.Message, db, bot, state: FSMContext):
    stock_codes = message.text.strip().split('\n')
    data = await state.get_data()
    
    await db.add_product(
        data['name'],
        data['price'],
        data['description'],
        stock_codes
    )
    
    await message.answer(
        f"✅ *Product Added Successfully!*\n\n"
        f"📦 Name: {data['name']}\n"
        f"💰 Price: ₹{data['price']}\n"
        f"📝 Description: {data['description']}\n"
        f"📊 Stock: {len(stock_codes)} units",
        reply_markup=admin_back_keyboard(),
        parse_mode="Markdown"
    )
    await state.clear()

async def edit_product_menu(callback: types.CallbackQuery, db, bot, state: FSMContext):
    product_id = callback.data.split(":")[1]
    await state.update_data(edit_product_id=product_id)
    
    await callback.message.edit_text(
        "✏️ *Edit Product*\n\n"
        "What would you like to edit?",
        reply_markup=admin_edit_product_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

async def admin_add_stock(callback: types.CallbackQuery, db, bot, state: FSMContext):
    product_id = callback.data.split(":")[1]
    await state.update_data(stock_product_id=product_id)
    
    await callback.message.edit_text(
        "📦 *Add Stock*\n\n"
        "Send me the stock codes (one per line):",
        reply_markup=cancel_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(AdminProductState.waiting_stock)
    await callback.answer()

async def process_add_stock(message: types.Message, db, bot, state: FSMContext):
    stock_codes = message.text.strip().split('\n')
    data = await state.get_data()
    
    await db.add_stock(data['stock_product_id'], stock_codes)
    
    await message.answer(
        f"✅ *Stock Added Successfully!*\n\n"
        f"Added {len(stock_codes)} new codes",
        reply_markup=admin_back_keyboard(),
        parse_mode="Markdown"
    )
    await state.clear()

async def admin_payments(callback: types.CallbackQuery, db, bot):
    if callback.from_user.id != Config.ADMIN_ID:
        await callback.answer("⛔️ Unauthorized!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "💳 *Payment Management*\n\n"
        f"Current UPI ID: `{Config.UPI_ID}`\n\n"
        "To change UPI ID, edit the .env file and restart the bot.",
        reply_markup=admin_back_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

async def admin_deposits(callback: types.CallbackQuery, db, bot):
    if callback.from_user.id != Config.ADMIN_ID:
        await callback.answer("⛔️ Unauthorized!", show_alert=True)
        return
    
    deposits = await db.get_pending_transactions("deposit")
    
    if not deposits:
        text = "💰 *Pending Deposits*\n\nNo pending deposits."
    else:
        text = f"💰 *Pending Deposits* ({len(deposits)})\n\n"
        for deposit in deposits:
            text += f"🆔 User: {deposit['user_id']}\n"
            text += f"💰 Amount: ₹{deposit['amount']}\n"
            text += f"🔢 UTR: {deposit['utr']}\n"
            text += f"⏰ Time: {deposit['created_at'].strftime('%Y-%m-%d %H:%M')}\n"
            text += f"📸 Screenshot ID: {deposit['screenshot_id']}\n"
            text += "─" * 20 + "\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=admin_approve_keyboard("deposit"),
        parse_mode="Markdown"
    )
    await callback.answer()

async def admin_orders(callback: types.CallbackQuery, db, bot):
    if callback.from_user.id != Config.ADMIN_ID:
        await callback.answer("⛔️ Unauthorized!", show_alert=True)
        return
    
    # Get pending UPI orders
    await callback.message.edit_text(
        "📦 *Pending Orders*\n\n"
        "No pending orders at the moment.",
        reply_markup=admin_back_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

async def admin_withdraws(callback: types.CallbackQuery, db, bot):
    if callback.from_user.id != Config.ADMIN_ID:
        await callback.answer("⛔️ Unauthorized!", show_alert=True)
        return
    
    withdraws = await db.get_pending_withdraws()
    
    if not withdraws:
        text = "💸 *Pending Withdrawals*\n\nNo pending withdrawals."
    else:
        text = f"💸 *Pending Withdrawals* ({len(withdraws)})\n\n"
        for withdraw in withdraws:
            text += f"🆔 User: {withdraw['user_id']}\n"
            text += f"💰 Amount: ₹{withdraw['amount']}\n"
            text += f"🏦 UPI ID: {withdraw['upi_id']}\n"
            text += f"⏰ Time: {withdraw['created_at'].strftime('%Y-%m-%d %H:%M')}\n"
            text += "─" * 20 + "\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=admin_approve_keyboard("withdraw"),
        parse_mode="Markdown"
    )
    await callback.answer()

async def admin_users(callback: types.CallbackQuery, db, bot):
    if callback.from_user.id != Config.ADMIN_ID:
        await callback.answer("⛔️ Unauthorized!", show_alert=True)
        return
    
    stats = await db.get_stats()
    await callback.message.edit_text(
        f"👥 *User Management*\n\n"
        f"Total Users: {stats['total_users']}\n\n"
        f"Feature coming soon: View individual user details",
        reply_markup=admin_back_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

async def admin_broadcast(callback: types.CallbackQuery, db, bot, state: FSMContext):
    if callback.from_user.id != Config.ADMIN_ID:
        await callback.answer("⛔️ Unauthorized!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📢 *Broadcast Message*\n\n"
        "Send me the message you want to broadcast to all users:\n\n"
        "You can use HTML formatting:\n"
        "<b>Bold</b>, <i>Italic</i>, <a href='https://example.com'>Link</a>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(AdminBroadcastState.waiting_message)
    await callback.answer()

async def process_broadcast(message: types.Message, db, bot, state: FSMContext):
    if message.from_user.id != Config.ADMIN_ID:
        return
    
    users = await db.db.users.find().to_list(length=None)
    success = 0
    failed = 0
    
    progress_msg = await message.answer(f"📢 Broadcasting to {len(users)} users...")
    
    for user in users:
        try:
            await bot.send_message(
                user['user_id'],
                message.text,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
            success += 1
        except:
            failed += 1
        
        # Avoid hitting rate limits
        if success % 20 == 0:
            await asyncio.sleep(1)
    
    await progress_msg.edit_text(
        f"✅ *Broadcast Complete*\n\n"
        f"✅ Sent: {success}\n"
        f"❌ Failed: {failed}",
        parse_mode="Markdown"
    )
    await state.clear()

def register_admin_handlers(dp: Dispatcher, db, bot):
    dp.callback_query.register(lambda c: admin_panel(c, db, bot), F.data == "admin_panel")
    dp.callback_query.register(lambda c: admin_products_menu(c, db, bot), F.data == "admin_products")
    dp.callback_query.register(lambda c: add_product_start(c, db, bot, None), F.data == "add_product")
    dp.callback_query.register(lambda c: edit_product_menu(c, db, bot, None), F.data.startswith("edit_product:"))
    dp.callback_query.register(lambda c: admin_add_stock(c, db, bot, None), F.data.startswith("add_stock:"))
    dp.callback_query.register(lambda c: admin_payments(c, db, bot), F.data == "admin_payments")
    dp.callback_query.register(lambda c: admin_deposits(c, db, bot), F.data == "admin_deposits")
    dp.callback_query.register(lambda c: admin_orders(c, db, bot), F.data == "admin_orders")
    dp.callback_query.register(lambda c: admin_withdraws(c, db, bot), F.data == "admin_withdraws")
    dp.callback_query.register(lambda c: admin_users(c, db, bot), F.data == "admin_users")
    dp.callback_query.register(lambda c: admin_broadcast(c, db, bot, None), F.data == "admin_broadcast")
    
    dp.message.register(lambda m: process_product_name(m, db, bot, None), AdminProductState.waiting_name)
    dp.message.register(lambda m: process_product_price(m, db, bot, None), AdminProductState.waiting_price)
    dp.message.register(lambda m: process_product_description(m, db, bot, None), AdminProductState.waiting_description)
    dp.message.register(lambda m: process_product_stock(m, db, bot, None), AdminProductState.waiting_stock)
    dp.message.register(lambda m: process_add_stock(m, db, bot, None), AdminProductState.waiting_stock)
    dp.message.register(lambda m: process_broadcast(m, db, bot, None), AdminBroadcastState.waiting_message)
