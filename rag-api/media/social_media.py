"""
Social Media Control

Automation for Twitter/X, Facebook, Instagram, LinkedIn, etc.
"""

from typing import Optional, Dict, Any, List
import os

try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False


class SocialMediaController:
    """Controls social media platforms."""
    
    def __init__(self, platform: str = "twitter"):
        """
        Initialize social media controller.
        
        Args:
            platform: Platform name ("twitter", "facebook", "instagram", "linkedin")
        """
        self.platform = platform
        
        if platform == "twitter":
            self.api_key = os.getenv("TWITTER_API_KEY")
            self.api_secret = os.getenv("TWITTER_API_SECRET")
            self.access_token = os.getenv("TWITTER_ACCESS_TOKEN")
            self.access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
            if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
                raise ValueError("Twitter API credentials are required")
        elif platform == "facebook":
            self.access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
            if not self.access_token:
                raise ValueError("FACEBOOK_ACCESS_TOKEN is required")
        elif platform == "instagram":
            self.access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
            if not self.access_token:
                raise ValueError("INSTAGRAM_ACCESS_TOKEN is required")
        elif platform == "linkedin":
            self.client_id = os.getenv("LINKEDIN_CLIENT_ID")
            self.client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
            self.access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
            if not all([self.client_id, self.client_secret, self.access_token]):
                raise ValueError("LinkedIn API credentials are required")
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    
    async def post(self, content: str, media_urls: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """
        Post content to social media.
        
        Args:
            content: Text content to post
            media_urls: Optional list of media URLs
            **kwargs: Platform-specific parameters
        
        Returns:
            Post information
        """
        if self.platform == "twitter":
            return await self._post_twitter(content, media_urls, **kwargs)
        elif self.platform == "facebook":
            return await self._post_facebook(content, media_urls, **kwargs)
        elif self.platform == "instagram":
            return await self._post_instagram(content, media_urls, **kwargs)
        elif self.platform == "linkedin":
            return await self._post_linkedin(content, media_urls, **kwargs)
        else:
            raise ValueError(f"Unsupported platform: {self.platform}")
    
    async def _post_twitter(self, content: str, media_urls: Optional[List[str]], **kwargs) -> Dict[str, Any]:
        """Post to Twitter/X."""
        if not HAS_AIOHTTP:
            raise ImportError("aiohttp is required. Install with: pip install aiohttp")
        
        # Twitter API v2
        url = "https://api.twitter.com/2/tweets"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {"text": content}
        
        # Add media if provided
        if media_urls:
            # Upload media first (simplified - in production use proper media upload)
            media_ids = []
            for media_url in media_urls:
                # This is simplified - actual implementation needs media upload endpoint
                media_ids.append(media_url)
            payload["media"] = {"media_ids": media_ids}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    error = await response.text()
                    raise Exception(f"Twitter API error: {error}")
    
    async def _post_facebook(self, content: str, media_urls: Optional[List[str]], **kwargs) -> Dict[str, Any]:
        """Post to Facebook."""
        if not HAS_AIOHTTP:
            raise ImportError("aiohttp is required")
        
        page_id = kwargs.get("page_id") or os.getenv("FACEBOOK_PAGE_ID")
        if not page_id:
            raise ValueError("Facebook page ID is required")
        
        url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
        params = {
            "message": content,
            "access_token": self.access_token
        }
        
        if media_urls:
            params["link"] = media_urls[0]
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.text()
                    raise Exception(f"Facebook API error: {error}")
    
    async def _post_instagram(self, content: str, media_urls: Optional[List[str]], **kwargs) -> Dict[str, Any]:
        """Post to Instagram."""
        if not HAS_AIOHTTP:
            raise ImportError("aiohttp is required")
        
        # Instagram requires media upload first
        if not media_urls:
            raise ValueError("Instagram posts require media")
        
        # Simplified - actual implementation needs proper Instagram Graph API flow
        url = "https://graph.instagram.com/v18.0/me/media"
        params = {
            "image_url": media_urls[0],
            "caption": content,
            "access_token": self.access_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params) as response:
                if response.status == 200:
                    creation_data = await response.json()
                    # Then publish
                    media_id = creation_data.get("id")
                    publish_url = f"https://graph.instagram.com/v18.0/me/media_publish"
                    publish_params = {
                        "creation_id": media_id,
                        "access_token": self.access_token
                    }
                    async with session.post(publish_url, params=publish_params) as publish_response:
                        if publish_response.status == 200:
                            return await publish_response.json()
                        else:
                            error = await publish_response.text()
                            raise Exception(f"Instagram publish error: {error}")
                else:
                    error = await response.text()
                    raise Exception(f"Instagram API error: {error}")
    
    async def _post_linkedin(self, content: str, media_urls: Optional[List[str]], **kwargs) -> Dict[str, Any]:
        """Post to LinkedIn."""
        if not HAS_AIOHTTP:
            raise ImportError("aiohttp is required")
        
        person_urn = kwargs.get("person_urn") or os.getenv("LINKEDIN_PERSON_URN")
        if not person_urn:
            raise ValueError("LinkedIn person URN is required")
        
        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        # Build share content
        share_content = {
            "shareCommentary": {
                "text": content
            },
            "shareMediaCategory": "NONE"
        }
        
        if media_urls:
            share_content["shareMediaCategory"] = "ARTICLE"
            share_content["media"] = [{"status": "READY", "originalUrl": url} for url in media_urls]
        
        payload = {
            "author": f"urn:li:person:{person_urn}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": share_content
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    error = await response.text()
                    raise Exception(f"LinkedIn API error: {error}")
    
    async def get_posts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent posts."""
        if self.platform == "twitter":
            return await self._get_twitter_posts(limit)
        elif self.platform == "facebook":
            return await self._get_facebook_posts(limit)
        else:
            raise ValueError(f"Get posts not implemented for {self.platform}")
    
    async def _get_twitter_posts(self, limit: int) -> List[Dict[str, Any]]:
        """Get Twitter posts."""
        if not HAS_AIOHTTP:
            raise ImportError("aiohttp is required")
        
        user_id = os.getenv("TWITTER_USER_ID")
        url = f"https://api.twitter.com/2/users/{user_id}/tweets"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        params = {
            "max_results": limit
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                else:
                    error = await response.text()
                    raise Exception(f"Twitter API error: {error}")
    
    async def _get_facebook_posts(self, limit: int) -> List[Dict[str, Any]]:
        """Get Facebook posts."""
        if not HAS_AIOHTTP:
            raise ImportError("aiohttp is required")
        
        page_id = os.getenv("FACEBOOK_PAGE_ID")
        url = f"https://graph.facebook.com/v18.0/{page_id}/posts"
        params = {
            "access_token": self.access_token,
            "limit": limit
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                else:
                    error = await response.text()
                    raise Exception(f"Facebook API error: {error}")


# Global instances
_social_media_controllers: Dict[str, SocialMediaController] = {}

def get_social_media_controller(platform: Optional[str] = None) -> SocialMediaController:
    """Get social media controller instance."""
    platform = platform or os.getenv("SOCIAL_MEDIA_PLATFORM", "twitter")
    
    if platform not in _social_media_controllers:
        _social_media_controllers[platform] = SocialMediaController(platform=platform)
    
    return _social_media_controllers[platform]

