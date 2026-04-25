import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from config import Config
from database import Database
from user_handlers import register_user_handlers
from admin_handlers import register_admin_handlers
from utils import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=Config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Initialize database
db = Database()

async def set_commands():
    """Set bot commands"""
    commands = [
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="help", description="Get help"),
    ]
    await bot.set_my_commands(commands)

async def main():
    """Main function to start the bot"""
    try:
        # Initialize database
        await db.init_db()
        logger.info("Database initialized")
        
        # Register handlers
        register_user_handlers(dp, db, bot)
        register_admin_handlers(dp, db, bot)
        logger.info("Handlers registered")
        
        # Set commands
        await set_commands()
        
        # Start polling
        logger.info("Bot started successfully")
        await dp.start_polling(bot, skip_updates=True)
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
