import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Bot Configuration
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
    
    # Database Configuration
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "ecommerce_bot")
    
    # Payment Configuration
    UPI_ID = os.getenv("UPI_ID", "example@okhdfcbank")
    SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "support")
    
    # Referral Configuration
    REFERRAL_PERCENT = 2
    REFERRAL_BONUS = 40
    
    # Cache Configuration
    CACHE_TTL = 300  # 5 minutes
    
    @classmethod
    def validate(cls):
        """Validate required configurations"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required")
        if not cls.ADMIN_ID:
            raise ValueError("ADMIN_ID is required")
        return True
