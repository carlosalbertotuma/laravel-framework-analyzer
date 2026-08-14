import re
from typing import Dict, Any, List

class ModelParser:
    @staticmethod
    def parse_model(content: str) -> Dict[str, Any]:
        fillable, guarded, relations = [], [], []
        
        # $fillable
        fill_match = re.search(r'protected\s+\$fillable\s*=\s*\[([^\]]+)\];', content)
        if fill_match:
            fillable = [item.strip().strip("'\"") for item in fill_match.group(1).split(',') if item.strip()]

        # $guarded
        guard_match = re.search(r'protected\s+\$guarded\s*=\s*\[([^\]]+)\];', content)
        if guard_match:
            guarded = [item.strip().strip("'\"") for item in guard_match.group(1).split(',') if item.strip()]

        # Relations (hasMany, belongsTo, etc.)
        for match in re.finditer(r'public\s+function\s+([A-Za-z0-9_]+)\s*\(\)\s*\{[^}]*\$this->(hasOne|hasMany|belongsTo|belongsToMany)\s*\(\s*([A-Za-z0-9_\\]+)::class', content):
            relations.append({
                "relation_name": match.group(1),
                "type": match.group(2),
                "target_model": match.group(3).split('\\')[-1]
            })

        return {
            "fillable": fillable,
            "guarded": guarded,
            "relations": relations
        }

class RepositoryParser:
    @staticmethod
    def parse_repository(content: str) -> Dict[str, Any]:
        model_class = None
        # Identifica model() { return Lead::class; } comum em repositórios Laravel/Krayin
        match = re.search(r'function\s+model\s*\(\)\s*\{[^}]*return\s+([A-Za-z0-9_\\]+)::class', content)
        if match:
            model_class = match.group(1).split('\\')[-1]
        
        methods = re.findall(r'public\s+function\s+([A-Za-z0-9_]+)', content)
        return {
            "bound_model": model_class,
            "methods": methods
        }

class ServiceParser:
    @staticmethod
    def parse_service(content: str) -> Dict[str, Any]:
        methods = re.findall(r'public\s+function\s+([A-Za-z0-9_]+)', content)
        return {"methods": methods}
