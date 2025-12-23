"""
Slack Integration

Slack bot for notifications and interactions.
"""
import os
from typing import Dict, Optional
try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False
    WebClient = None
    SlackApiError = Exception


class SlackIntegration:
    """Handles Slack bot integration"""
    
    def __init__(self):
        """Initialize Slack integration"""
        self.slack_token = os.getenv("SLACK_BOT_TOKEN")
        self.client = None
        
        if self.slack_token:
            try:
                self.client = WebClient(token=self.slack_token)
            except Exception as e:
                print(f"Warning: Slack client initialization failed: {e}")
    
    def send_message(
        self,
        channel: str,
        text: str,
        blocks: Optional[list] = None
    ) -> Dict:
        """
        Send message to Slack channel.
        
        Args:
            channel: Slack channel ID or name
            text: Message text
            blocks: Optional Slack block kit blocks
            
        Returns:
            Dict with success status
        """
        if not SLACK_AVAILABLE:
            raise Exception("slack-sdk not installed. Install with: pip install slack-sdk")
        
        if not self.client:
            raise Exception("Slack client not initialized. Set SLACK_BOT_TOKEN environment variable.")
        
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=text,
                blocks=blocks
            )
            
            return {
                "success": True,
                "ts": response["ts"],
                "channel": channel
            }
        except SlackApiError as e:
            raise Exception(f"Slack API error: {e.response['error']}")
    
    def send_notification(
        self,
        channel: str,
        title: str,
        message: str,
        color: str = "good"  # good, warning, danger
    ) -> Dict:
        """Send formatted notification to Slack"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": title
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message
                }
            }
        ]
        
        return self.send_message(channel, title, blocks)


# Global Slack integration instance
slack_integration = SlackIntegration()

