"""
AX Tree extraction from Playwright.
Extracts accessibility tree for element selection and interaction.
"""
from playwright.async_api import Page
from typing import List, Dict, Optional


async def extract_ax_tree(page: Page) -> List[Dict]:
    """
    Extract accessibility tree from Playwright page.
    
    Args:
        page: Playwright Page object
        
    Returns:
        List of accessibility tree nodes with role, name, state, and bounds
    """
    try:
        # Use Playwright's accessibility snapshot
        snapshot = await page.accessibility.snapshot()
        
        def process_node(node: Dict, parent_id: Optional[str] = None) -> List[Dict]:
            """Recursively process accessibility tree nodes"""
            nodes = []
            
            if node is None:
                return nodes
            
            # Extract node information
            node_data = {
                "id": node.get("id", ""),
                "role": node.get("role", ""),
                "name": node.get("name", ""),
                "value": node.get("value", ""),
                "description": node.get("description", ""),
                "checked": node.get("checked"),
                "pressed": node.get("pressed"),
                "selected": node.get("selected"),
                "disabled": node.get("disabled"),
                "expanded": node.get("expanded"),
                "level": node.get("level"),
                "parent_id": parent_id
            }
            
            # Get bounding box if available
            if "boundingBox" in node:
                bbox = node["boundingBox"]
                node_data["bounds"] = {
                    "x": bbox.get("x", 0),
                    "y": bbox.get("y", 0),
                    "width": bbox.get("width", 0),
                    "height": bbox.get("height", 0)
                }
            
            nodes.append(node_data)
            
            # Process children
            if "children" in node:
                for child in node["children"]:
                    nodes.extend(process_node(child, node_data["id"]))
            
            return nodes
        
        # Process root node
        if snapshot:
            return process_node(snapshot)
        else:
            return []
            
    except Exception as e:
        print(f"Error extracting AX tree: {e}")
        return []


def filter_ax_tree(
    ax_tree: List[Dict],
    role: Optional[str] = None,
    name: Optional[str] = None,
    state: Optional[Dict] = None
) -> List[Dict]:
    """
    Filter accessibility tree by role, name, or state.
    
    Args:
        ax_tree: List of AX tree nodes
        role: Filter by role (e.g., "button", "textbox")
        name: Filter by accessible name (partial match)
        state: Filter by state (e.g., {"disabled": False})
        
    Returns:
        Filtered list of nodes
    """
    filtered = ax_tree
    
    if role:
        filtered = [n for n in filtered if n.get("role") == role]
    
    if name:
        name_lower = name.lower()
        filtered = [n for n in filtered if name_lower in n.get("name", "").lower()]
    
    if state:
        for key, value in state.items():
            filtered = [n for n in filtered if n.get(key) == value]
    
    return filtered


def find_element_by_ax(
    ax_tree: List[Dict],
    role: Optional[str] = None,
    name: Optional[str] = None,
    exact_name: bool = False
) -> Optional[Dict]:
    """
    Find element in AX tree by role and/or name.
    
    Args:
        ax_tree: List of AX tree nodes
        role: Element role (e.g., "button")
        name: Element name (accessible name)
        exact_name: If True, match name exactly; if False, partial match
        
    Returns:
        First matching node or None
    """
    filtered = ax_tree
    
    if role:
        filtered = [n for n in filtered if n.get("role") == role]
    
    if name:
        if exact_name:
            filtered = [n for n in filtered if n.get("name") == name]
        else:
            name_lower = name.lower()
            filtered = [n for n in filtered if name_lower in n.get("name", "").lower()]
    
    return filtered[0] if filtered else None

