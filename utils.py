import logging
import re
import asyncio
from datetime import datetime, timedelta
from config import Config

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler()
        ]
    )

def format_currency(amount):
    """Format amount in Indian Rupees"""
    return f"₹{amount:,.2f}"

def generate_referral_link(user_id):
    """Generate referral link for user"""
    return f"https://t.me/YourBotUsername?start={user_id}"

def validate_utr(utr):
    """Validate UTR number format"""
    # UTR is typically 12-16 digits or alphanumeric
    pattern = r'^[A-Z0-9]{12,16}$'
    return bool(re.match(pattern, utr.upper()))

def validate_upi_id(upi_id):
    """Validate UPI ID format"""
    pattern = r'^[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{3,}$'
    return bool(re.match(pattern, upi_id))

def calculate_referral_commission(amount):
    """Calculate referral commission"""
    return (amount * Config.REFERRAL_PERCENT) / 100

def format_order_summary(order_data):
    """Format order summary for display"""
    summary = f"🛒 *Order Summary*\n\n"
    summary += f"📦 Product: {order_data['product_name']}\n"
    summary += f"🔢 Quantity: {order_data['quantity']}\n"
    summary += f"💰 Price per unit: {format_currency(order_data['price'])}\n"
    summary += f"💵 *Total: {format_currency(order_data['total'])}*\n\n"
    return summary

def format_user_profile(user_data):
    """Format user profile for display"""
    profile = f"👤 *User Profile*\n\n"
    profile += f"🆔 ID: `{user_data['user_id']}`\n"
    profile += f"💰 Wallet: {format_currency(user_data['wallet'])}\n"
    profile += f"📅 Joined: {user_data['joined_at'].strftime('%Y-%m-%d')}\n"
    if 'referrals' in user_data:
        profile += f"👥 Referrals: {len(user_data['referrals'])}\n"
        profile += f"⭐️ Earnings: {format_currency(user_data.get('referral_earnings', 0))}"
    return profile

def calculate_statistics(orders, users):
    """Calculate various statistics"""
    stats = {
        'total_orders': len(orders),
        'total_users': len(users),
        'total_revenue': sum(order.get('total_price', 0) for order in orders),
        'avg_order_value': 0,
        'today_orders': 0,
        'today_revenue': 0,
        'week_orders': 0,
        'week_revenue': 0
    }
    
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = datetime.now() - timedelta(days=7)
    
    for order in orders:
        order_date = order.get('created_at')
        if order_date:
            if order_date >= today:
                stats['today_orders'] += 1
                stats['today_revenue'] += order.get('total_price', 0)
            if order_date >= week_ago:
                stats['week_orders'] += 1
                stats['week_revenue'] += order.get('total_price', 0)
    
    if stats['total_orders'] > 0:
        stats['avg_order_value'] = stats['total_revenue'] / stats['total_orders']
    
    return stats

def is_admin(user_id):
    """Check if user is admin"""
    return user_id == Config.ADMIN_ID

def sanitize_input(text):
    """Sanitize user input to prevent injection"""
    # Remove any potentially harmful characters
    return re.sub(r'[<>\"\'%;()&+]', '', text)

def format_time_ago(timestamp):
    """Format timestamp as 'time ago' string"""
    now = datetime.now()
    diff = now - timestamp
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "just now"

def truncate_text(text, max_length=100):
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def create_backup_filename(prefix="backup"):
    """Create a backup filename with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.json"

def validate_amount(amount):
    """Validate amount is positive number"""
    try:
        amount = float(amount)
        return amount > 0 and amount <= 50000  # Max 50,000 INR
    except:
        return False

def mask_sensitive_info(text):
    """Mask sensitive information in logs"""
    # Mask UPI IDs
    text = re.sub(r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{3,}', '[UPI_ID]', text)
    # Mask UTR numbers
    text = re.sub(r'[A-Z0-9]{12,16}', '[UTR]', text)
    return text

def validate_product_price(price):
    """Validate product price"""
    try:
        price = float(price)
        return price > 0 and price <= 100000  # Max 100,000 INR
    except:
        return False

def calculate_profit_margin(cost_price, selling_price):
    """Calculate profit margin percentage"""
    if cost_price <= 0:
        return 0
    return ((selling_price - cost_price) / cost_price) * 100

def generate_order_id():
    """Generate unique order ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_num = __import__('random').randint(1000, 9999)
    return f"ORD_{timestamp}_{random_num}"

def parse_quantity_input(text):
    """Parse quantity from user input"""
    try:
        quantity = int(text.strip())
        if 1 <= quantity <= 100:  # Reasonable limits
            return quantity
        return None
    except:
        return None

def format_phone_number(phone):
    """Format Indian phone number"""
    # Remove any non-digit characters
    phone = re.sub(r'\D', '', phone)
    if len(phone) == 10:
        return f"+91 {phone[:5]} {phone[5:]}"
    elif len(phone) == 12 and phone.startswith('91'):
        return f"+91 {phone[2:7]} {phone[7:]}"
    return phone

def calculate_tax(amount, tax_percentage=18):
    """Calculate GST tax"""
    return (amount * tax_percentage) / 100

def format_bold(text):
    """Format text as bold for markdown"""
    return f"*{text}*"

def format_code(text):
    """Format text as monospace code"""
    return f"`{text}`"

def create_success_response(action, details=""):
    """Create standardized success response"""
    response = f"✅ *{action} Successful!*"
    if details:
        response += f"\n\n{details}"
    return response

def create_error_response(error_type, details=""):
    """Create standardized error response"""
    response = f"❌ *{error_type} Failed!*"
    if details:
        response += f"\n\n{details}"
    return response

def get_payment_status_emoji(status):
    """Get emoji for payment status"""
    status_emoji = {
        'pending': '⏳',
        'completed': '✅',
        'failed': '❌',
        'refunded': '🔄'
    }
    return status_emoji.get(status, '❓')

def validate_screenshot(message):
    """Validate if message contains a photo"""
    if message.photo:
        return message.photo[-1].file_id
    return None

def escape_markdown(text):
    """Escape special characters for markdown"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

def split_long_message(text, max_length=4000):
    """Split long message into chunks"""
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    for line in text.split('\n'):
        if len(current_chunk) + len(line) + 1 > max_length:
            chunks.append(current_chunk)
            current_chunk = line
        else:
            if current_chunk:
                current_chunk += '\n' + line
            else:
                current_chunk = line
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

class Logger:
    """Custom logger wrapper"""
    def __init__(self, name):
        self.logger = logging.getLogger(name)
    
    def info(self, message):
        self.logger.info(mask_sensitive_info(message))
    
    def error(self, message):
        self.logger.error(mask_sensitive_info(message))
    
    def warning(self, message):
        self.logger.warning(mask_sensitive_info(message))
    
    def debug(self, message):
        self.logger.debug(mask_sensitive_info(message))

async def rate_limit_delay(user_id, cache_dict, delay_seconds=1):
    """Simple rate limiting"""
    last_call = cache_dict.get(user_id, 0)
    now = asyncio.get_event_loop().time()
    
    if now - last_call < delay_seconds:
        await asyncio.sleep(delay_seconds - (now - last_call))
    
    cache_dict[user_id] = asyncio.get_event_loop().time()

def format_date(date_input):
    """Format date object to string"""
    if isinstance(date_input, datetime):
        return date_input.strftime("%Y-%m-%d %H:%M:%S")
    return str(date_input)

def calculate_discount(price, discount_percent):
    """Calculate discounted price"""
    discount_amount = (price * discount_percent) / 100
    return price - discount_amount

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def extract_numbers(text):
    """Extract all numbers from text"""
    numbers = re.findall(r'\d+', text)
    return [int(num) for num in numbers]

def format_size(bytes_size):
    """Format bytes to human readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"

def truncate_middle(text, max_length=50):
    """Truncate text from middle"""
    if len(text) <= max_length:
        return text
    half = (max_length - 3) // 2
    return text[:half] + "..." + text[-half:]

def is_valid_pincode(pincode):
    """Validate Indian pincode"""
    pattern = r'^[1-9][0-9]{5}$'
    return bool(re.match(pattern, str(pincode)))

def generate_random_string(length=10):
    """Generate random string"""
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def format_number_with_commas(number):
    """Format number with commas for Indian numbering system"""
    num_str = str(int(number))
    # Indian numbering system (lakhs, crores)
    if len(num_str) <= 3:
        return num_str
    last_three = num_str[-3:]
    rest = num_str[:-3]
    if rest:
        last_three = "," + last_three
    result = ""
    while rest:
        result = "," + rest[-2:] + result
        rest = rest[:-2]
    result = result[1:] + last_three
    return result

def merge_dicts(dict1, dict2):
    """Merge two dictionaries"""
    result = dict1.copy()
    result.update(dict2)
    return result

def chunk_list(lst, chunk_size):
    """Split list into chunks"""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def retry_async(func, retries=3, delay=1):
    """Decorator for async retry logic"""
    async def wrapper(*args, **kwargs):
        last_error = None
        for attempt in range(retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < retries - 1:
                    await asyncio.sleep(delay * (attempt + 1))
        raise last_error
    return wrapper
