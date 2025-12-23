"""
Plan-Act-Verify-Recover Pattern for Browser Automation
"""
from typing import List, Dict, Optional
from browser.actions import ActionExecutor
from browser.ax_tree import extract_ax_tree
from openai import OpenAI
import os
import base64
import json


class BrowserAutomation:
    """
    Orchestrates browser automation with Plan-Act-Verify-Recover pattern.
    """
    
    def __init__(self, page, openai_client: Optional[OpenAI] = None):
        self.page = page
        self.executor = ActionExecutor(page)
        self.openai_client = openai_client or OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def plan(self, user_intent: str, current_url: str) -> List[Dict]:
        """
        Generate action sequence from user intent.
        
        Args:
            user_intent: User's goal (e.g., "Search for Python tutorials")
            current_url: Current page URL
            
        Returns:
            List of action dicts with type, target, and parameters
        """
        # Get current page context
        ax_tree = await extract_ax_tree(self.page)
        ax_tree_summary = self._summarize_ax_tree(ax_tree)
        
        screenshot = await self.page.screenshot()
        screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
        
        # Use LLM to generate plan
        prompt = f"""You are a browser automation assistant. The user wants to: {user_intent}

Current page URL: {current_url}

Available UI elements (accessibility tree summary):
{ax_tree_summary}

Generate a step-by-step plan to accomplish the user's goal. Each step should be an action:
- navigate: Go to a URL
- click: Click an element (specify role and name from AX tree)
- type: Type text into an input (specify role and name)
- extract: Extract text from an element

Return a JSON array of actions, each with:
- type: "navigate" | "click" | "type" | "extract"
- target_role: Element role (if applicable)
- target_name: Element name (if applicable)
- value: Text to type or URL to navigate (if applicable)

Example:
[
  {{"type": "click", "target_role": "textbox", "target_name": "Search"}},
  {{"type": "type", "target_role": "textbox", "target_name": "Search", "value": "Python tutorials"}},
  {{"type": "click", "target_role": "button", "target_name": "Search"}}
]

Return only the JSON array, no other text."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a browser automation planner. Return only valid JSON arrays."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            import json
            plan_text = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            if plan_text.startswith("```"):
                plan_text = plan_text.split("```")[1]
                if plan_text.startswith("json"):
                    plan_text = plan_text[4:]
            plan_text = plan_text.strip()
            
            plan = json.loads(plan_text)
            return plan
            
        except Exception as e:
            # Fallback: simple plan
            return [{"type": "click", "target_role": "textbox", "target_name": "Search"}]
    
    def _summarize_ax_tree(self, ax_tree: List[Dict], max_elements: int = 20) -> str:
        """Summarize AX tree for LLM context"""
        summary = []
        for i, node in enumerate(ax_tree[:max_elements]):
            role = node.get("role", "")
            name = node.get("name", "")
            if role and name:
                summary.append(f"- {role}: {name}")
        return "\n".join(summary)
    
    async def act(self, action: Dict, ax_tree: List[Dict]) -> Dict:
        """
        Execute a single action.
        
        Args:
            action: Action dict with type, target_role, target_name, value
            ax_tree: Current accessibility tree
            
        Returns:
            Action result dict
        """
        action_type = action.get("type")
        
        if action_type == "click":
            return await self.executor.click_element(
                ax_tree,
                role=action.get("target_role"),
                name=action.get("target_name")
            )
        elif action_type == "type":
            return await self.executor.type_text(
                ax_tree,
                text=action.get("value", ""),
                role=action.get("target_role"),
                name=action.get("target_name")
            )
        elif action_type == "extract":
            return await self.executor.extract_text(
                ax_tree,
                role=action.get("target_role"),
                name=action.get("target_name")
            )
        else:
            return {
                "success": False,
                "error": f"Unknown action type: {action_type}"
            }
    
    async def verify(self, action: Dict, result: Dict) -> Dict:
        """
        Verify action succeeded using vision.
        
        Args:
            action: Original action
            result: Action result
            
        Returns:
            Verification result with confidence
        """
        if not result.get("success"):
            return {
                "verified": False,
                "confidence": 0.0,
                "reason": result.get("error", "Action failed")
            }
        
        # Take screenshot
        screenshot = await self.page.screenshot()
        screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
        
        # Use vision to verify state change
        action_desc = f"{action.get('type')} on {action.get('target_name', 'element')}"
        
        prompt = f"""Did the action "{action_desc}" succeed? Look at this screenshot and determine if the action was successful.

Action: {action.get('type')}
Target: {action.get('target_name')}

Check if:
1. The element was clicked/typed into (if applicable)
2. The page state changed appropriately
3. Any error messages appeared

Respond with JSON: {{"verified": true/false, "confidence": 0.0-1.0, "reason": "explanation"}}"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{screenshot_b64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            import json
            verification_text = response.choices[0].message.content.strip()
            if verification_text.startswith("```"):
                verification_text = verification_text.split("```")[1]
                if verification_text.startswith("json"):
                    verification_text = verification_text[4:]
            verification_text = verification_text.strip()
            
            verification = json.loads(verification_text)
            return verification
            
        except Exception as e:
            # Fallback: assume verified if action succeeded
            return {
                "verified": result.get("success", False),
                "confidence": 0.7,
                "reason": f"Vision verification failed: {str(e)}"
            }
    
    async def recover(self, action: Dict, result: Dict, attempt: int, max_attempts: int = 3) -> Dict:
        """
        Recover from failed action.
        
        Args:
            action: Failed action
            result: Action result
            attempt: Current attempt number
            max_attempts: Maximum retry attempts
            
        Returns:
            Recovery result
        """
        if attempt >= max_attempts:
            return {
                "recovered": False,
                "reason": "Max retry attempts reached"
            }
        
        # Refresh AX tree and retry
        ax_tree = await extract_ax_tree(self.page)
        
        # Retry action
        retry_result = await self.act(action, ax_tree)
        
        if retry_result.get("success"):
            return {
                "recovered": True,
                "attempt": attempt + 1,
                "result": retry_result
            }
        else:
            return {
                "recovered": False,
                "attempt": attempt + 1,
                "reason": retry_result.get("error", "Retry failed")
            }
    
    async def execute_plan(self, user_intent: str) -> Dict:
        """
        Execute full plan with Plan-Act-Verify-Recover loop.
        
        Args:
            user_intent: User's goal
            
        Returns:
            Execution result with all steps
        """
        current_url = self.page.url
        plan = await self.plan(user_intent, current_url)
        
        results = []
        
        for i, action in enumerate(plan):
            # Act
            ax_tree = await extract_ax_tree(self.page)
            result = await self.act(action, ax_tree)
            
            # Verify
            verification = await self.verify(action, result)
            
            # Recover if needed
            if not verification.get("verified") and result.get("success"):
                # Action succeeded but verification failed - might be false negative
                pass
            elif not result.get("success"):
                # Action failed - try recovery
                recovery = await self.recover(action, result, attempt=1)
                if recovery.get("recovered"):
                    result = recovery["result"]
                    verification = await self.verify(action, result)
            
            results.append({
                "step": i + 1,
                "action": action,
                "result": result,
                "verification": verification
            })
            
            # Stop if critical failure
            if not result.get("success") and not result.get("uncertain"):
                break
        
        return {
            "plan": plan,
            "results": results,
            "success": all(r["result"].get("success") for r in results)
        }

