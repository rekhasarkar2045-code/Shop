from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from bson import ObjectId
import logging
from config import Config

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        
    async def init_db(self):
        """Initialize database connection"""
        try:
            self.client = AsyncIOMotorClient(Config.MONGO_URI)
            self.db = self.client[Config.DATABASE_NAME]
            
            # Create indexes
            await self.db.users.create_index("user_id", unique=True)
            await self.db.products.create_index("name")
            await self.db.orders.create_index("order_id")
            await self.db.transactions.create_index("utr", unique=True, sparse=True)
            
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    # User operations
    async def get_user(self, user_id):
        return await self.db.users.find_one({"user_id": user_id})
    
    async def create_user(self, user_id, username, first_name, referrer_id=None):
        user_data = {
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "wallet": 0,
            "joined_at": datetime.now(),
            "referred_by": referrer_id,
            "referrals": [],
            "referral_earnings": 0,
            "total_earned": 0
        }
        
        # Handle referral bonus
        if referrer_id and referrer_id != user_id:
            referrer = await self.get_user(referrer_id)
            if referrer:
                bonus = Config.REFERRAL_BONUS
                await self.update_wallet(referrer_id, bonus)
                await self.db.users.update_one(
                    {"user_id": referrer_id},
                    {"$push": {"referrals": user_id}, "$inc": {"referral_earnings": bonus, "total_earned": bonus}}
                )
        
        await self.db.users.insert_one(user_data)
        return user_data
    
    async def update_wallet(self, user_id, amount):
        return await self.db.users.update_one(
            {"user_id": user_id},
            {"$inc": {"wallet": amount}}
        )
    
    # Product operations
    async def add_product(self, name, price, description, stock_codes=None):
        product = {
            "name": name,
            "price": price,
            "description": description,
            "stock": stock_codes if stock_codes else [],
            "created_at": datetime.now(),
            "active": True
        }
        result = await self.db.products.insert_one(product)
        return result.inserted_id
    
    async def get_products(self, active_only=True):
        query = {"active": True} if active_only else {}
        cursor = self.db.products.find(query)
        return await cursor.to_list(length=None)
    
    async def get_product(self, product_id):
        return await self.db.products.find_one({"_id": ObjectId(product_id)})
    
    async def update_product(self, product_id, data):
        return await self.db.products.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": data}
        )
    
    async def delete_product(self, product_id):
        return await self.db.products.delete_one({"_id": ObjectId(product_id)})
    
    async def add_stock(self, product_id, codes):
        return await self.db.products.update_one(
            {"_id": ObjectId(product_id)},
            {"$push": {"stock": {"$each": codes}}}
        )
    
    async def get_stock_code(self, product_id):
        product = await self.get_product(product_id)
        if product and product.get("stock"):
            code = product["stock"].pop(0)
            await self.update_product(product_id, {"stock": product["stock"]})
            return code
        return None
    
    # Order operations
    async def create_order(self, user_id, product_id, quantity, total_price, payment_method):
        order = {
            "order_id": f"ORD_{datetime.now().timestamp()}",
            "user_id": user_id,
            "product_id": product_id,
            "quantity": quantity,
            "total_price": total_price,
            "payment_method": payment_method,
            "status": "pending",
            "payment_status": "pending",
            "created_at": datetime.now(),
            "delivery_code": None
        }
        result = await self.db.orders.insert_one(order)
        return result.inserted_id
    
    async def complete_order(self, order_id, delivery_code):
        await self.db.orders.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {"status": "completed", "payment_status": "completed", "delivery_code": delivery_code}}
        )
    
    async def get_user_orders(self, user_id, limit=10):
        cursor = self.db.orders.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    # Transaction operations
    async def create_transaction(self, user_id, utr, amount, screenshot_id, transaction_type):
        transaction = {
            "user_id": user_id,
            "utr": utr,
            "amount": amount,
            "screenshot_id": screenshot_id,
            "type": transaction_type,
            "status": "pending",
            "created_at": datetime.now()
        }
        await self.db.transactions.insert_one(transaction)
        return transaction
    
    async def get_pending_transactions(self, transaction_type):
        cursor = self.db.transactions.find({"type": transaction_type, "status": "pending"})
        return await cursor.to_list(length=None)
    
    async def approve_transaction(self, utr):
        transaction = await self.db.transactions.find_one({"utr": utr})
        if transaction:
            await self.db.transactions.update_one({"utr": utr}, {"$set": {"status": "approved"}})
            if transaction["type"] == "deposit":
                await self.update_wallet(transaction["user_id"], transaction["amount"])
            return transaction
        return None
    
    async def check_utr_exists(self, utr):
        return await self.db.transactions.find_one({"utr": utr}) is not None
    
    # Withdraw operations
    async def create_withdraw_request(self, user_id, amount, upi_id):
        withdraw = {
            "user_id": user_id,
            "amount": amount,
            "upi_id": upi_id,
            "status": "pending",
            "created_at": datetime.now()
        }
        await self.db.withdraws.insert_one(withdraw)
    
    async def get_pending_withdraws(self):
        cursor = self.db.withdraws.find({"status": "pending"})
        return await cursor.to_list(length=None)
    
    async def approve_withdraw(self, withdraw_id):
        withdraw = await self.db.withdraws.find_one({"_id": ObjectId(withdraw_id)})
        if withdraw:
            await self.db.withdraws.update_one({"_id": ObjectId(withdraw_id)}, {"$set": {"status": "approved"}})
            await self.update_wallet(withdraw["user_id"], -withdraw["amount"])
            return withdraw
        return None
    
    # Stats operations
    async def get_stats(self):
        total_users = await self.db.users.count_documents({})
        total_orders = await self.db.orders.count_documents({"status": "completed"})
        total_revenue_cursor = self.db.orders.aggregate([
            {"$match": {"status": "completed"}},
            {"$group": {"_id": None, "total": {"$sum": "$total_price"}}}
        ])
        total_revenue = await total_revenue_cursor.to_list(length=1)
        
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_orders_cursor = self.db.orders.aggregate([
            {"$match": {"status": "completed", "created_at": {"$gte": today}}},
            {"$group": {"_id": None, "total": {"$sum": "$total_price"}}}
        ])
        today_income = await today_orders_cursor.to_list(length=1)
        
        return {
            "total_users": total_users,
            "total_orders": total_orders,
            "total_revenue": total_revenue[0]["total"] if total_revenue else 0,
            "today_income": today_income[0]["total"] if today_income else 0
  }
