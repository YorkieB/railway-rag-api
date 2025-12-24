"""
Login Automation Helper
Intelligently finds and fills login forms.
"""
from playwright.async_api import Page
from typing import Dict, Optional, List
from browser.ax_tree import extract_ax_tree, find_element_by_ax
import asyncio


class LoginHelper:
    """
    Helper class for automating login flows.
    """
    
    def __init__(self, page: Page):
        self.page = page
    
    async def find_login_fields(self) -> Dict:
        """
        Find username/email and password fields on the page.
        
        Returns:
            Dict with found fields and their details
        """
        ax_tree = await extract_ax_tree(self.page)
        
        # Common patterns for username/email fields
        username_patterns = [
            "username", "email", "user", "login", "account", 
            "user name", "e-mail", "userid", "user id"
        ]
        
        # Common patterns for password fields
        password_patterns = [
            "password", "pass", "pwd", "passphrase"
        ]
        
        # Find all textboxes
        textboxes = [n for n in ax_tree if n.get("role") == "textbox"]
        
        username_field = None
        password_field = None
        
        # Try to find username/email field
        for pattern in username_patterns:
            for textbox in textboxes:
                name = textbox.get("name", "").lower()
                if pattern in name:
                    username_field = textbox
                    break
            if username_field:
                break
        
        # If not found by name, try to find by input type, ID, or placeholder
        if not username_field:
            # Try to find by common input types and IDs
            try:
                # Try input#email first (common pattern)
                email_by_id = await self.page.query_selector('input#email')
                if email_by_id:
                    username_field = {
                        "role": "textbox",
                        "name": "email",
                        "id": "email",
                        "selector": "input#email"
                    }
                else:
                    # Try other email input patterns
                    email_inputs = await self.page.query_selector_all('input[type="email"], input[type="text"][name*="user"], input[type="text"][name*="email"], input[type="text"][id*="user"], input[type="text"][id*="email"]')
                    if email_inputs:
                        # Get the first email input's accessibility info
                        for input_elem in email_inputs[:1]:
                            # Try to get accessible name, id, or name attribute
                            elem_id = await input_elem.get_attribute("id") or ""
                            elem_name = await input_elem.get_attribute("name") or ""
                            name = elem_name or elem_id or ""
                            input_type = await input_elem.get_attribute("type") or "text"
                            
                            username_field = {
                                "role": "textbox",
                                "name": name,
                                "id": elem_id,
                                "selector": f"input#{elem_id}" if elem_id else (f"input[type='{input_type}']" if input_type == "email" else f"input[name='{elem_name}']")
                            }
                            break
            except Exception as e:
                print(f"Error finding email field: {e}")
                pass
        
        # Find password field
        for pattern in password_patterns:
            for textbox in textboxes:
                name = textbox.get("name", "").lower()
                if pattern in name:
                    password_field = textbox
                    break
            if password_field:
                break
        
        # If password not found, try by input type or ID
        if not password_field:
            try:
                # Try input#password first (common pattern)
                password_by_id = await self.page.query_selector('input#password')
                if password_by_id:
                    password_field = {
                        "role": "textbox",
                        "name": "password",
                        "id": "password",
                        "selector": "input#password"
                    }
                else:
                    # Try all password inputs
                    password_inputs = await self.page.query_selector_all('input[type="password"]')
                    if password_inputs:
                        for input_elem in password_inputs[:1]:
                            elem_id = await input_elem.get_attribute("id") or ""
                            elem_name = await input_elem.get_attribute("name") or ""
                            name = elem_name or elem_id or "password"
                            password_field = {
                                "role": "textbox",
                                "name": name,
                                "id": elem_id,
                                "selector": f"input#{elem_id}" if elem_id else "input[type='password']"
                            }
                            break
            except Exception as e:
                print(f"Error finding password field: {e}")
                pass
        
        return {
            "username_field": username_field,
            "password_field": password_field,
            "found": username_field is not None and password_field is not None
        }
    
    async def fill_login_form(
        self,
        username: str,
        password: str
    ) -> Dict:
        """
        Fill login form with username and password.
        
        Args:
            username: Username or email
            password: Password
            
        Returns:
            Dict with success status and details
        """
        fields = await self.find_login_fields()
        
        if not fields["found"]:
            return {
                "success": False,
                "error": "Could not find login fields on the page",
                "fields_found": {
                    "username": fields["username_field"] is not None,
                    "password": fields["password_field"] is not None
                }
            }
        
        results = []
        
        # Fill username field
        if fields["username_field"]:
            try:
                username_field = fields["username_field"]
                
                # Try using ID first (most reliable)
                if "id" in username_field and username_field["id"]:
                    await self.page.fill(f'input#{username_field["id"]}', username)
                # Try using accessible name
                elif "name" in username_field and username_field["name"]:
                    await self.page.get_by_role("textbox", name=username_field["name"]).fill(username)
                # Fallback to selector if available
                elif "selector" in username_field:
                    await self.page.fill(username_field["selector"], username)
                # Try common selectors
                else:
                    # Try email input by type
                    email_input = await self.page.query_selector('input[type="email"]')
                    if email_input:
                        await email_input.fill(username)
                    else:
                        # Try input with id="email"
                        email_by_id = await self.page.query_selector('input#email')
                        if email_by_id:
                            await email_by_id.fill(username)
                        else:
                            # Try first text input
                            inputs = await self.page.query_selector_all('input[type="text"]')
                            if inputs:
                                await inputs[0].fill(username)
                
                results.append({
                    "field": "username",
                    "success": True
                })
            except Exception as e:
                results.append({
                    "field": "username",
                    "success": False,
                    "error": str(e)
                })
        
        # Fill password field
        if fields["password_field"]:
            try:
                password_field = fields["password_field"]
                
                # Try using ID first (most reliable)
                if "id" in password_field and password_field["id"]:
                    await self.page.fill(f'input#{password_field["id"]}', password)
                # Try using accessible name
                elif "name" in password_field and password_field["name"]:
                    await self.page.get_by_role("textbox", name=password_field["name"]).fill(password)
                # Fallback to selector if available
                elif "selector" in password_field:
                    await self.page.fill(password_field["selector"], password)
                # Fallback to password input type
                else:
                    # Try input#password
                    password_by_id = await self.page.query_selector('input#password')
                    if password_by_id:
                        await password_by_id.fill(password)
                    else:
                        await self.page.fill('input[type="password"]', password)
                
                results.append({
                    "field": "password",
                    "success": True
                })
            except Exception as e:
                results.append({
                    "field": "password",
                    "success": False,
                    "error": str(e)
                })
        
        # Check if all fields were filled successfully
        all_success = all(r["success"] for r in results)
        
        return {
            "success": all_success,
            "results": results,
            "fields_found": fields["found"]
        }
    
    async def submit_login(self) -> Dict:
        """
        Find and click the login/submit button.
        
        Returns:
            Dict with success status
        """
        ax_tree = await extract_ax_tree(self.page)
        
        # Common patterns for login/submit buttons
        login_button_patterns = [
            "sign in", "login", "log in", "submit", "continue",
            "sign in with", "log in with", "enter"
        ]
        
        # Try to find button by name
        login_button = None
        for pattern in login_button_patterns:
            login_button = find_element_by_ax(ax_tree, role="button", name=pattern)
            if login_button:
                break
        
        # If not found, try to find submit button
        if not login_button:
            login_button = find_element_by_ax(ax_tree, role="button", name="submit")
        
        # If still not found, try input[type="submit"]
        if not login_button:
            try:
                submit_inputs = await self.page.query_selector_all('input[type="submit"], button[type="submit"]')
                if submit_inputs:
                    login_button = {
                        "role": "button",
                        "name": await submit_inputs[0].get_attribute("value") or "Submit",
                        "selector": "input[type='submit']"
                    }
            except:
                pass
        
        if not login_button:
            return {
                "success": False,
                "error": "Could not find login button"
            }
        
        try:
            # Click using accessible name
            if "name" in login_button and login_button["name"]:
                await self.page.get_by_role("button", name=login_button["name"]).click()
            # Fallback to selector
            elif "selector" in login_button:
                await self.page.click(login_button["selector"])
            # Fallback to first submit button
            else:
                await self.page.click('input[type="submit"], button[type="submit"]')
            
            # Wait a bit for page to load
            await asyncio.sleep(1)
            
            return {
                "success": True,
                "button_clicked": login_button.get("name", "Submit")
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def complete_login(
        self,
        username: str,
        password: str
    ) -> Dict:
        """
        Complete full login flow: find fields, fill form, and submit.
        
        Args:
            username: Username or email
            password: Password
            
        Returns:
            Dict with complete login result
        """
        # Step 1: Fill login form
        fill_result = await self.fill_login_form(username, password)
        
        if not fill_result["success"]:
            return {
                "success": False,
                "step": "fill_form",
                "error": fill_result.get("error", "Failed to fill login form"),
                "details": fill_result
            }
        
        # Step 2: Submit login
        submit_result = await self.submit_login()
        
        if not submit_result["success"]:
            return {
                "success": False,
                "step": "submit",
                "error": submit_result.get("error", "Failed to submit login"),
                "fill_result": fill_result,
                "submit_result": submit_result
            }
        
        # Step 3: Wait and check if login was successful
        await asyncio.sleep(2)
        current_url = self.page.url
        page_title = await self.page.title()
        
        return {
            "success": True,
            "fill_result": fill_result,
            "submit_result": submit_result,
            "current_url": current_url,
            "page_title": page_title,
            "message": "Login completed successfully"
        }

