"""
Custom Rules System - Core implementation
"""

from typing import Dict, Any, List, Callable

class ExtractionRule:
    def __init__(self, 
                 name: str,
                 field: str,
                 condition: Callable[[str, Dict[str, Any]], bool],
                 action: Callable[[str, Dict[str, Any]], Any],
                 priority: int = 0):
        self.name = name
        self.field = field
        self.condition = condition
        self.action = action
        self.priority = priority
    
    def can_apply(self, html: str, data: Dict[str, Any]) -> bool:
        try:
            return self.condition(html, data)
        except Exception:
            return False
    
    def apply(self, html: str, data: Dict[str, Any]) -> Any:
        try:
            return self.action(html, data)
        except Exception as e:
            print(f"❌ Error applying rule {self.name}: {e}")
            return None

class CustomExtractor:
    def __init__(self):
        self.pre_hooks: List[Callable] = []
        self.post_hooks: List[Callable] = []
    
    def add_pre_hook(self, hook: Callable[[str, Dict[str, Any]], tuple]):
        self.pre_hooks.append(hook)
    
    def add_post_hook(self, hook: Callable[[Dict[str, Any]], Dict[str, Any]]):
        self.post_hooks.append(hook)
    
    def extract_with_rules(self, html: str, data: Dict[str, Any]) -> Dict[str, Any]:
        # Run pre-hooks
        for hook in self.pre_hooks:
            try:
                html, data = hook(html, data)
            except Exception as e:
                print(f"❌ Error in pre-hook: {e}")
        
        # Run post-hooks
        for hook in self.post_hooks:
            try:
                data = hook(data)
            except Exception as e:
                print(f"❌ Error in post-hook: {e}")
        
        return data