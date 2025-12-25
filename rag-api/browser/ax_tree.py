"""
AX Tree Extraction

Extracts and processes accessibility tree from browser pages.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class AXTreeNode:
    """
    Accessibility tree node.
    
    Represents an element in the accessibility tree with its properties.
    """
    role: str
    name: Optional[str] = None
    value: Optional[str] = None
    description: Optional[str] = None
    state: Optional[Dict[str, bool]] = None
    children: Optional[List['AXTreeNode']] = None
    selector: Optional[str] = None  # CSS selector for targeting
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "role": self.role,
            "name": self.name,
            "value": self.value,
            "description": self.description,
            "state": self.state,
            "selector": self.selector
        }
        
        if self.children:
            result["children"] = [child.to_dict() for child in self.children]
        
        return result


def extract_ax_tree(snapshot: Dict[str, Any], include_hidden: bool = False) -> Optional[AXTreeNode]:
    """
    Extract accessibility tree from Playwright snapshot.
    
    Args:
        snapshot: Playwright accessibility snapshot
        include_hidden: Include hidden elements
        
    Returns:
        Root AXTreeNode or None
    """
    if not snapshot:
        return None
    
    return _parse_node(snapshot, include_hidden)


def _parse_node(node_data: Dict[str, Any], include_hidden: bool) -> Optional[AXTreeNode]:
    """Parse a single node from snapshot."""
    if not node_data:
        return None
    
    # Skip hidden nodes unless requested
    if not include_hidden and node_data.get("ignored", False):
        return None
    
    # Extract properties
    role = node_data.get("role", "generic")
    name = node_data.get("name")
    value = node_data.get("value")
    description = node_data.get("description")
    
    # Extract state
    state = {}
    for key in ["checked", "disabled", "expanded", "focused", "pressed", "selected"]:
        if key in node_data:
            state[key] = node_data[key]
    
    # Parse children
    children = []
    if "children" in node_data:
        for child_data in node_data["children"]:
            child_node = _parse_node(child_data, include_hidden)
            if child_node:
                children.append(child_node)
    
    # Generate selector (simplified - in production, use more robust method)
    selector = _generate_selector(node_data)
    
    return AXTreeNode(
        role=role,
        name=name,
        value=value,
        description=description,
        state=state if state else None,
        children=children if children else None,
        selector=selector
    )


def _generate_selector(node_data: Dict[str, Any]) -> Optional[str]:
    """
    Generate CSS selector for node.
    
    This is a simplified version. In production, use Playwright's
    element handle to generate more reliable selectors.
    """
    # Try to use name or role for selector
    name = node_data.get("name")
    role = node_data.get("role", "")
    
    if name:
        # Try to create selector from name (simplified)
        return f'[aria-label="{name}"]'
    
    # Fallback to role-based selector
    if role and role != "generic":
        return f'[role="{role}"]'
    
    return None


def filter_ax_tree(
    root: AXTreeNode,
    role: Optional[str] = None,
    name: Optional[str] = None,
    state: Optional[Dict[str, bool]] = None
) -> List[AXTreeNode]:
    """
    Filter accessibility tree by criteria.
    
    Args:
        root: Root node to filter
        role: Filter by role
        name: Filter by name (partial match)
        state: Filter by state properties
        
    Returns:
        List of matching nodes
    """
    results = []
    
    def _traverse(node: AXTreeNode):
        # Check filters
        match = True
        
        if role and node.role != role:
            match = False
        
        if name and (not node.name or name.lower() not in node.name.lower()):
            match = False
        
        if state and node.state:
            for key, value in state.items():
                if node.state.get(key) != value:
                    match = False
                    break
        
        if match:
            results.append(node)
        
        # Traverse children
        if node.children:
            for child in node.children:
                _traverse(child)
    
    if root:
        _traverse(root)
    
    return results


def find_interactive_elements(root: AXTreeNode) -> List[AXTreeNode]:
    """
    Find all interactive elements in AX tree.
    
    Returns:
        List of interactive nodes (buttons, links, inputs, etc.)
    """
    interactive_roles = {
        "button", "link", "textbox", "checkbox", "radio", "combobox",
        "slider", "tab", "menuitem", "option", "switch"
    }
    
    results = []
    
    def _traverse(node: AXTreeNode):
        if node.role in interactive_roles:
            results.append(node)
        
        if node.children:
            for child in node.children:
                _traverse(child)
    
    if root:
        _traverse(root)
    
    return results

