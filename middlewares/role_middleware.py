
from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from utils.db_api import user_commands

class RoleMiddleware(BaseMiddleware):
    """
    Middleware to check user roles and permissions
    """
    
    async def on_pre_process_message(self, message: types.Message, data: dict):
        """
        This handler is called when dispatcher receives a message
        """
        # Get user from DB or create if doesn't exist
        user_id = message.from_user.id
        user = await user_commands.get_user(user_id)
        
        if not user:
            # If user is new, create with default client role
            user = await user_commands.add_user(
                user_id=user_id,
                full_name=message.from_user.full_name,
                username=message.from_user.username,
                role="client"
            )
        
        # Add user data to middleware data for handlers to access
        data["user"] = user
        data["role"] = user["role"]
    
    async def on_pre_process_callback_query(self, callback_query: types.CallbackQuery, data: dict):
        """
        This handler is called when dispatcher receives a callback query
        """
        # Get user from DB or create if doesn't exist
        user_id = callback_query.from_user.id
        user = await user_commands.get_user(user_id)
        
        if not user:
            # If user is new, create with default client role
            user = await user_commands.add_user(
                user_id=user_id,
                full_name=callback_query.from_user.full_name,
                username=callback_query.from_user.username,
                role="client"
            )
        
        # Add user data to middleware data for handlers to access
        data["user"] = user
        data["role"] = user["role"]
