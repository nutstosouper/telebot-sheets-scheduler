
from utils.db_api.google_sheets import get_sheet, write_to_sheet
from datetime import datetime, timedelta

# Sheet names for subscriptions and payments
SUBSCRIPTIONS_SHEET = "Subscriptions"
PAYMENTS_SHEET = "Payments"  # New sheet for payment validation

async def get_subscription(user_id):
    """Get subscription for a specific user"""
    subscriptions = await get_sheet(SUBSCRIPTIONS_SHEET)
    user_id_str = str(user_id)
    
    for subscription in subscriptions:
        if str(subscription.get('user_id')) == user_id_str:
            return subscription
    
    return None

async def create_subscription(user_id, days=30, trial=False, referrer_id=None):
    """Create a new subscription for a user (admin only)"""
    subscriptions = await get_sheet(SUBSCRIPTIONS_SHEET)
    
    # Check if subscription already exists
    for subscription in subscriptions:
        if str(subscription.get('user_id')) == str(user_id):
            # Update existing subscription
            return await extend_subscription(user_id, days)
    
    # Create new subscription
    start_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    
    new_subscription = {
        'user_id': str(user_id),
        'start_date': start_date,
        'end_date': end_date,
        'trial': 'yes' if trial else 'no',
        'referrer_id': str(referrer_id) if referrer_id else ''
    }
    
    subscriptions.append(new_subscription)
    await write_to_sheet(SUBSCRIPTIONS_SHEET, subscriptions)
    
    return new_subscription

async def extend_subscription(user_id, days):
    """Extend an existing subscription by a certain number of days"""
    subscriptions = await get_sheet(SUBSCRIPTIONS_SHEET)
    user_id_str = str(user_id)
    updated = False
    
    for i, subscription in enumerate(subscriptions):
        if str(subscription.get('user_id')) == user_id_str:
            # Get current end date
            current_end_date = subscription.get('end_date')
            
            try:
                # Parse current end date
                if current_end_date:
                    end_date = datetime.strptime(current_end_date, "%Y-%m-%d")
                else:
                    end_date = datetime.now()
                
                # Add days to end date
                new_end_date = (end_date + timedelta(days=days)).strftime("%Y-%m-%d")
                subscriptions[i]['end_date'] = new_end_date
                
                # Update trial status to 'no' if extending
                subscriptions[i]['trial'] = 'no'
                
                updated = True
                break
            except Exception as e:
                # If date parsing fails, set a new date from today
                new_end_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
                subscriptions[i]['end_date'] = new_end_date
                subscriptions[i]['trial'] = 'no'
                updated = True
                break
    
    if updated:
        await write_to_sheet(SUBSCRIPTIONS_SHEET, subscriptions)
        return subscriptions[i]
    
    # If subscription doesn't exist, create a new one
    return await create_subscription(user_id, days)

async def check_subscription_status(user_id):
    """Check if an admin has an active subscription"""
    subscription = await get_subscription(user_id)
    
    if not subscription:
        return {
            'active': False,
            'days_left': 0,
            'trial': False,
            'message': 'У вас нет активной подписки'
        }
    
    try:
        end_date = datetime.strptime(subscription.get('end_date'), "%Y-%m-%d")
        now = datetime.now()
        
        # Calculate days left
        days_left = (end_date - now).days
        
        if days_left < 0:
            return {
                'active': False,
                'days_left': 0,
                'trial': False,
                'message': 'Ваша подписка истекла'
            }
        
        # Check if trial
        is_trial = subscription.get('trial') == 'yes'
        
        return {
            'active': True,
            'days_left': days_left,
            'trial': is_trial,
            'end_date': subscription.get('end_date'),
            'message': f'{"Пробная подписка" if is_trial else "Подписка"} активна еще {days_left} дней (до {subscription.get("end_date")})'
        }
    except Exception as e:
        return {
            'active': False,
            'days_left': 0,
            'trial': False,
            'message': f'Ошибка при проверке подписки: {str(e)}'
        }

async def create_trial(user_id, days=7):
    """Create a trial subscription for an admin"""
    return await create_subscription(user_id, days, trial=True)

async def process_referral(referrer_id):
    """Process a referral - extend referrer's subscription by 30 days"""
    return await extend_subscription(referrer_id, 30)

async def get_all_subscriptions():
    """Get all subscriptions"""
    return await get_sheet(SUBSCRIPTIONS_SHEET)

async def is_admin_subscribed(user_id):
    """Check if an admin has an active subscription"""
    status = await check_subscription_status(user_id)
    return status['active']

# New functions for payment validation
async def record_payment(user_id, plan_months, amount, payment_method="manual"):
    """Record a subscription payment"""
    # Initialize payments sheet if not exists
    payments = await get_sheet(PAYMENTS_SHEET)
    
    payment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payment_id = str(len(payments) + 1)
    
    new_payment = {
        'id': payment_id,
        'user_id': str(user_id),
        'plan_months': plan_months,
        'amount': amount,
        'payment_date': payment_date,
        'payment_method': payment_method,
        'verified': 'no'  # Default to unverified
    }
    
    payments.append(new_payment)
    await write_to_sheet(PAYMENTS_SHEET, payments)
    
    return new_payment

async def verify_payment(payment_id):
    """Verify a payment and activate subscription"""
    payments = await get_sheet(PAYMENTS_SHEET)
    verified = False
    user_id = None
    plan_months = 0
    
    for i, payment in enumerate(payments):
        if payment.get('id') == payment_id:
            payments[i]['verified'] = 'yes'
            verified = True
            user_id = payment.get('user_id')
            plan_months = int(payment.get('plan_months', 1))
            break
    
    if verified and user_id:
        await write_to_sheet(PAYMENTS_SHEET, payments)
        # Convert months to days
        days = plan_months * 30
        # Extend subscription
        return await extend_subscription(user_id, days)
    
    return None

async def get_user_payments(user_id):
    """Get all payments for a user"""
    payments = await get_sheet(PAYMENTS_SHEET)
    user_payments = []
    
    for payment in payments:
        if str(payment.get('user_id')) == str(user_id):
            user_payments.append(payment)
    
    return user_payments

async def check_payment_verified(user_id, plan_months=None):
    """Check if user has a verified payment for the specified plan"""
    payments = await get_user_payments(user_id)
    
    for payment in payments:
        if payment.get('verified') == 'yes':
            if plan_months is None or int(payment.get('plan_months', 0)) == plan_months:
                return True
    
    return False
