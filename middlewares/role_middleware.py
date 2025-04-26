
from typing import Dict, Any, Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from utils.db_api import user_commands
from utils.db_api import subscription_commands

class RoleMiddleware(BaseMiddleware):
    """
    Middleware to check user roles and permissions
    """
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """
        This handler is called when dispatcher receives a message or callback query
        """
        # Get user from event
        if isinstance(event, Message):
            user_id = event.from_user.id
            full_name = event.from_user.full_name
            username = event.from_user.username
        else:  # CallbackQuery
            user_id = event.from_user.id
            full_name = event.from_user.full_name
            username = event.from_user.username
        
        # Get user from DB or create if doesn't exist
        user = await user_commands.get_user(user_id)
        
        if not user:
            # If user is new, create with default client role
            user = await user_commands.add_user(
                user_id=user_id,
                full_name=full_name,
                username=username,
                role="client"  # Default role is client
            )
        
        # If we still couldn't get or create the user (due to sheet issues),
        # use a default user object to prevent errors
        if not user:
            user = {
                'user_id': user_id,
                'username': username or '',
                'full_name': full_name or '',
                'role': 'client'  # Default role
            }
        
        # Check subscription status if user is an admin
        if user["role"] == "admin":
            subscription_status = await subscription_commands.check_subscription_status(user_id)
            data["has_subscription"] = subscription_status["active"]
        else:
            data["has_subscription"] = True  # Clients don't need subscription
            
        # Add user data to middleware data for handlers to access
        data["user"] = user
        data["role"] = user["role"]
        
        # Call the handler with the updated data
        return await handler(event, data)
