"""
Memory Templates

Pre-defined templates for common memory types.
"""
from typing import Dict, List, Optional
from datetime import datetime
import uuid


class MemoryTemplate:
    """Template for creating memories"""
    
    def __init__(
        self,
        template_id: str,
        name: str,
        description: str,
        memory_type: str,
        fields: List[Dict]
    ):
        """
        Initialize memory template.
        
        Args:
            template_id: Unique template identifier
            name: Template name
            description: Template description
            memory_type: Type of memory this template creates
            fields: List of field definitions
        """
        self.template_id = template_id
        self.name = name
        self.description = description
        self.memory_type = memory_type
        self.fields = fields
        self.created_at = datetime.now()
    
    def create_memory(self, user_id: str, field_values: Dict, project_id: Optional[str] = None) -> str:
        """
        Create memory from template.
        
        Args:
            user_id: User identifier
            field_values: Dict mapping field names to values
            project_id: Optional project identifier
            
        Returns:
            Memory content string
        """
        # Build memory content from template fields
        content_parts = []
        for field in self.fields:
            field_name = field["name"]
            field_value = field_values.get(field_name, "")
            if field_value:
                content_parts.append(f"{field['label']}: {field_value}")
        
        return "\n".join(content_parts)


# In-memory template storage
memory_templates: Dict[str, MemoryTemplate] = {}


class MemoryTemplateManager:
    """Manages memory templates"""
    
    def __init__(self):
        """Initialize template manager with default templates"""
        self._initialize_default_templates()
    
    def _initialize_default_templates(self):
        """Initialize default memory templates"""
        # Person template
        person_template = MemoryTemplate(
            template_id="person",
            name="Person",
            description="Template for remembering information about a person",
            memory_type="fact",
            fields=[
                {"name": "name", "label": "Name", "type": "text", "required": True},
                {"name": "role", "label": "Role", "type": "text", "required": False},
                {"name": "contact", "label": "Contact", "type": "text", "required": False},
                {"name": "notes", "label": "Notes", "type": "textarea", "required": False}
            ]
        )
        memory_templates["person"] = person_template
        
        # Meeting template
        meeting_template = MemoryTemplate(
            template_id="meeting",
            name="Meeting",
            description="Template for meeting notes and decisions",
            memory_type="decision",
            fields=[
                {"name": "date", "label": "Date", "type": "date", "required": True},
                {"name": "attendees", "label": "Attendees", "type": "text", "required": False},
                {"name": "topics", "label": "Topics Discussed", "type": "textarea", "required": False},
                {"name": "decisions", "label": "Decisions", "type": "textarea", "required": False},
                {"name": "action_items", "label": "Action Items", "type": "textarea", "required": False}
            ]
        )
        memory_templates["meeting"] = meeting_template
        
        # Preference template
        preference_template = MemoryTemplate(
            template_id="preference",
            name="Preference",
            description="Template for user preferences",
            memory_type="preference",
            fields=[
                {"name": "category", "label": "Category", "type": "text", "required": True},
                {"name": "preference", "label": "Preference", "type": "textarea", "required": True},
                {"name": "context", "label": "Context", "type": "textarea", "required": False}
            ]
        )
        memory_templates["preference"] = preference_template
    
    def create_template(
        self,
        name: str,
        description: str,
        memory_type: str,
        fields: List[Dict]
    ) -> Dict:
        """Create new memory template"""
        template_id = str(uuid.uuid4())
        template = MemoryTemplate(template_id, name, description, memory_type, fields)
        memory_templates[template_id] = template
        
        return {
            "template_id": template_id,
            "name": name,
            "description": description,
            "memory_type": memory_type,
            "fields": fields
        }
    
    def list_templates(self) -> List[Dict]:
        """List all available templates"""
        return [
            {
                "template_id": template.template_id,
                "name": template.name,
                "description": template.description,
                "memory_type": template.memory_type,
                "field_count": len(template.fields)
            }
            for template in memory_templates.values()
        ]
    
    def get_template(self, template_id: str) -> Optional[MemoryTemplate]:
        """Get template by ID"""
        return memory_templates.get(template_id)


# Global template manager
memory_template_manager = MemoryTemplateManager()

