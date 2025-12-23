"""
Zapier Integration

Webhook-based integration with Zapier for automation workflows.
"""
from typing import Dict, Optional
from datetime import datetime
import uuid


class ZapierIntegration:
    """Handles Zapier webhook integration"""
    
    def __init__(self):
        """Initialize Zapier integration"""
        self.webhooks: Dict[str, Dict] = {}
    
    def register_webhook(
        self,
        user_id: str,
        webhook_url: str,
        event_type: str,  # query, memory_created, document_uploaded, etc.
        filters: Optional[Dict] = None
    ) -> Dict:
        """
        Register Zapier webhook.
        
        Args:
            user_id: User identifier
            webhook_url: Zapier webhook URL
            event_type: Type of event to trigger webhook
            filters: Optional filters for events
            
        Returns:
            Dict with webhook_id and details
        """
        webhook_id = str(uuid.uuid4())
        self.webhooks[webhook_id] = {
            "webhook_id": webhook_id,
            "user_id": user_id,
            "webhook_url": webhook_url,
            "event_type": event_type,
            "filters": filters or {},
            "created_at": datetime.now().isoformat(),
            "active": True
        }
        
        return {
            "webhook_id": webhook_id,
            "status": "registered",
            "event_type": event_type
        }
    
    def trigger_webhook(
        self,
        event_type: str,
        data: Dict,
        user_id: Optional[str] = None
    ) -> Dict:
        """
        Trigger webhooks for an event.
        
        Args:
            event_type: Type of event
            data: Event data payload
            user_id: Optional user ID filter
            
        Returns:
            Dict with triggered webhooks count
        """
        triggered_count = 0
        
        for webhook_id, webhook in self.webhooks.items():
            if not webhook.get("active"):
                continue
            
            if webhook["event_type"] != event_type:
                continue
            
            if user_id and webhook["user_id"] != user_id:
                continue
            
            # In production, would send HTTP POST to webhook_url
            # For now, just track that it would be triggered
            triggered_count += 1
        
        return {
            "event_type": event_type,
            "triggered_count": triggered_count,
            "total_webhooks": len(self.webhooks)
        }


# Global Zapier integration instance
zapier_integration = ZapierIntegration()

