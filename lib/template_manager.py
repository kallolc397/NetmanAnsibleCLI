"""
Template management module for the Network Device Management tool.

This module handles Jinja2 templates for network device configurations.
"""
import os
import yaml
import json
import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

class TemplateManager:
    """Manages configuration templates."""
    
    def __init__(self, templates_dir="templates"):
        """Initialize with the templates directory."""
        self.templates_dir = templates_dir
        self._ensure_dir_exists()
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add functions to the Jinja2 environment
        self.env.globals['now'] = lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _ensure_dir_exists(self):
        """Ensure templates directory exists."""
        os.makedirs(self.templates_dir, exist_ok=True)
    
    def list_templates(self):
        """
        List available templates.
        
        Returns:
            list: List of template dictionaries
        """
        try:
            templates = []
            
            for file_path in Path(self.templates_dir).glob('*.j2'):
                template_name = file_path.stem
                
                # Try to extract description from template
                description = "No description available"
                with open(file_path, 'r') as f:
                    content = f.read()
                    # Look for a description comment in the first few lines
                    for line in content.split('\n')[:5]:
                        if line.strip().startswith('{#') and 'description:' in line.lower():
                            description = line.split('description:', 1)[1].strip().rstrip('#}').strip()
                            break
                
                templates.append({
                    'name': template_name,
                    'path': str(file_path),
                    'description': description
                })
            
            return templates
        except Exception as e:
            print(f"Error listing templates: {str(e)}")
            return []
    
    def render_template(self, template_name, vars_file=None):
        """
        Render a template with variables.
        
        Args:
            template_name (str): Name of the template (without .j2 extension)
            vars_file (str, optional): Path to a JSON/YAML variables file
            
        Returns:
            str: Rendered template content or None if failed
        """
        try:
            # Load template
            template = self.env.get_template(f"{template_name}.j2")
            
            # Load variables
            variables = {}
            if vars_file:
                if not os.path.exists(vars_file):
                    raise FileNotFoundError(f"Variables file {vars_file} not found")
                
                with open(vars_file, 'r') as f:
                    if vars_file.endswith('.json'):
                        variables = json.load(f)
                    elif vars_file.endswith(('.yml', '.yaml')):
                        variables = yaml.safe_load(f)
                    else:
                        raise ValueError("Variables file must be JSON or YAML")
            
            # Render template
            return template.render(**variables)
        except Exception as e:
            print(f"Error rendering template: {str(e)}")
            return None
    
    def get_template_content(self, template_name):
        """
        Get the raw content of a template.
        
        Args:
            template_name (str): Name of the template (without .j2 extension)
            
        Returns:
            str: Template content or None if failed
        """
        try:
            template_path = os.path.join(self.templates_dir, f"{template_name}.j2")
            
            if not os.path.exists(template_path):
                return None
            
            with open(template_path, 'r') as f:
                return f.read()
        except Exception as e:
            print(f"Error getting template: {str(e)}")
            return None
