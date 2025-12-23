"""
Form Auto-Fill

Automatically fills forms using saved credentials and data.
"""
from typing import Dict, List, Optional
from browser.session import BrowserSession
from windows.credentials import credential_manager


class FormFiller:
    """Handles automatic form filling"""
    
    def __init__(self, browser_session: BrowserSession):
        """
        Initialize form filler.
        
        Args:
            browser_session: Browser session instance
        """
        self.browser_session = browser_session
        self.page = browser_session.page
    
    async def fill_form(
        self,
        form_data: Dict[str, str],
        credential_name: Optional[str] = None
    ) -> Dict:
        """
        Fill form with provided data or saved credentials.
        
        Args:
            form_data: Dict mapping field names/selectors to values
            credential_name: Optional credential name to load from storage
            
        Returns:
            Dict with filled fields count and status
        """
        filled_count = 0
        errors = []
        
        # Load credentials if specified
        if credential_name:
            credential = credential_manager.get_credential(credential_name)
            if credential:
                form_data.update(credential.get("data", {}))
        
        # Fill each field
        for selector, value in form_data.items():
            try:
                # Try to find element by various selectors
                element = await self.page.query_selector(selector)
                if not element:
                    # Try by name, id, placeholder, label
                    element = await self.page.query_selector(f'[name="{selector}"]') or \
                              await self.page.query_selector(f'#{selector}') or \
                              await self.page.query_selector(f'[placeholder="{selector}"]')
                
                if element:
                    tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
                    
                    if tag_name == "input":
                        input_type = await element.get_attribute("type")
                        if input_type in ["text", "email", "password", "tel", "url"]:
                            await element.fill(value)
                            filled_count += 1
                        elif input_type == "checkbox" or input_type == "radio":
                            if value.lower() in ["true", "1", "yes", "checked"]:
                                await element.check()
                                filled_count += 1
                    elif tag_name == "textarea":
                        await element.fill(value)
                        filled_count += 1
                    elif tag_name == "select":
                        await element.select_option(value)
                        filled_count += 1
                else:
                    errors.append(f"Field not found: {selector}")
            except Exception as e:
                errors.append(f"Error filling {selector}: {str(e)}")
        
        return {
            "filled_count": filled_count,
            "total_fields": len(form_data),
            "errors": errors,
            "success": len(errors) == 0
        }

