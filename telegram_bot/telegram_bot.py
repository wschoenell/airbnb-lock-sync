import os
import requests


class TelegramBot:
    """Send messages via Telegram bot."""
    
    def __init__(self, token=None):
        """
        Initialize Telegram bot.
        
        Args:
            token (str): Telegram bot token. If None, reads from TELEGRAM_TOKEN env var.
        """
        self.token = token or os.getenv("TELEGRAM_TOKEN")
        if not self.token:
            raise ValueError("Telegram token not provided. Set TELEGRAM_TOKEN environment variable.")
        
        self.base_url = f"https://api.telegram.org/bot{self.token}"
    
    def send_message(self, chat_id, text, parse_mode=None):
        """
        Send a message to a Telegram chat or multiple chats.
        
        Args:
            chat_id (str or int or list): Telegram chat ID(s) to send message to.
                                         Can be a single ID, comma-separated string, or list.
            text (str): Message text to send
            parse_mode (str, optional): Parse mode for the message ('Markdown' or 'HTML')
        
        Returns:
            dict or list: Response from Telegram API. If multiple chat_ids, returns list of responses.
        
        Raises:
            requests.RequestException: If the request fails
        """
        # Parse chat_ids
        chat_ids = self._parse_chat_ids(chat_id)
        
        responses = []
        for cid in chat_ids:
            url = f"{self.base_url}/sendMessage"
            
            payload = {
                "chat_id": cid,
                "text": text
            }
            
            if parse_mode:
                payload["parse_mode"] = parse_mode
            
            try:
                response = requests.post(url, json=payload, timeout=10)
                response.raise_for_status()
                responses.append(response.json())
            except requests.RequestException as e:
                print(f"Error sending Telegram message to chat_id {cid}: {e}")
                responses.append({"ok": False, "error": str(e), "chat_id": cid})
        
        # Return single response if only one chat_id, otherwise return list
        return responses[0] if len(responses) == 1 else responses
    
    def _parse_chat_ids(self, chat_id):
        """
        Parse chat_id input into a list of chat IDs.
        
        Args:
            chat_id (str or int or list): Single ID, comma-separated string, or list
        
        Returns:
            list: List of chat IDs as strings
        """
        if isinstance(chat_id, list):
            return [str(cid).strip() for cid in chat_id]
        elif isinstance(chat_id, str):
            # Handle comma-separated values
            if ',' in chat_id:
                return [cid.strip() for cid in chat_id.split(',') if cid.strip()]
            return [chat_id.strip()]
        else:
            return [str(chat_id)]
    
    def get_updates(self, offset=None, limit=100, timeout=0):
        """
        Get updates from Telegram bot (useful for getting chat_id).
        
        Args:
            offset (int, optional): Identifier of the first update to be returned
            limit (int, optional): Limits the number of updates to be retrieved
            timeout (int, optional): Timeout in seconds for long polling
        
        Returns:
            dict: Response from Telegram API with updates
        """
        url = f"{self.base_url}/getUpdates"
        
        params = {
            "limit": limit,
            "timeout": timeout
        }
        
        if offset:
            params["offset"] = offset
        
        try:
            response = requests.get(url, params=params, timeout=timeout + 10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error getting Telegram updates: {e}")
            raise


def send_telegram_message(chat_id=None, message=None, parse_mode=None):
    """
    Convenience function to send a Telegram message.
    
    Args:
        chat_id (str or int or list, optional): Telegram chat ID(s). 
                                                Can be comma-separated string, list, or single ID.
                                                If None, reads from TELEGRAM_CHAT_ID env var.
        message (str): Message to send
        parse_mode (str, optional): Parse mode ('Markdown' or 'HTML')
    
    Returns:
        dict or list: Response from Telegram API, or None if token/chat_id not configured
    """
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        print("Warning: TELEGRAM_TOKEN not set, skipping Telegram notification")
        return None
    
    # Get chat_id from env var if not provided
    if chat_id is None:
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not chat_id:
        print("Warning: TELEGRAM_CHAT_ID not set, skipping Telegram notification")
        return None
    
    bot = TelegramBot(token)
    return bot.send_message(chat_id, message, parse_mode)


if __name__ == "__main__":
    # Example usage
    bot = TelegramBot()
    
    # Get chat ID (send a message to your bot first, then run this)
    print("Getting updates to find your chat_id...")
    updates = bot.get_updates()
    
    if updates.get("result"):
        for update in updates["result"]:
            if "message" in update:
                chat_id = update["message"]["chat"]["id"]
                print(f"Found chat_id: {chat_id}")
                
                # Send a test message
                response = bot.send_message(chat_id, "Hello from Airbnb Lock Sync! 🔐")
                print(f"Message sent: {response}")
                break
    else:
        print("No updates found. Send a message to your bot first, then run this script again.")
