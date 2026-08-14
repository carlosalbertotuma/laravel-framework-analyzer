import os
import re
from typing import Dict, List, Optional, Any

try:
    from tree_sitter import Language, Parser
    import tree_sitter_php
    PHP_LANGUAGE = Language(tree_sitter_php.language_php())
    TREE_SITTER_AVAILABLE = True
except Exception:
    TREE_SITTER_AVAILABLE = False

class ASTEngine:
    def __init__(self):
        self.ts_available = TREE_SITTER_AVAILABLE
        if self.ts_available:
            self.parser = Parser()
            self.parser.set_language(PHP_LANGUAGE)

    def parse_file(self, file_path: str) -> Optional[Any]:
        if not os.path.isfile(file_path):
            return None
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            if self.ts_available:
                return self.parser.parse(content)
        except Exception:
            return None
        return None

    @staticmethod
    def extract_use_statements(content: str) -> Dict[str, str]:
        """Extrai mapeamento de alias -> FQCN (Fully Qualified Class Name)."""
        uses = {}
        pattern = re.compile(r'use\s+([A-Za-z0-9_\\]+)(?:\s+as\s+([A-Za-z0-9_]+))?\s*;')
        for match in pattern.finditer(content):
            fqcn = match.group(1).lstrip('\\')
            alias = match.group(2) if match.group(2) else fqcn.split('\\')[-1]
            uses[alias] = fqcn
        return uses

    @staticmethod
    def extract_namespace(content: str) -> Optional[str]:
        match = re.search(r'namespace\s+([A-Za-z0-9_\\]+)\s*;', content)
        return match.group(1).lstrip('\\') if match else None
