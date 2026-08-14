import os
from typing import Dict, List

class ProjectScanner:
    def __init__(self, root_dir: str, include_vendor: bool = False, include_tests: bool = False):
        self.root_dir = os.path.abspath(root_dir)
        self.include_vendor = include_vendor
        self.include_tests = include_tests
        self.ignored_dirs = {".git", "node_modules", "storage", "bootstrap/cache"}
        if not include_vendor:
            self.ignored_dirs.add("vendor")
        if not include_tests:
            self.ignored_dirs.add("tests")

    def scan(self) -> Dict[str, List[str]]:
        inventory = {
            "routes": [],
            "controllers": [],
            "requests": [],
            "models": [],
            "repositories": [],
            "services": [],
            "middleware": [],
            "frontend": [],
            "all_php": []
        }

        for root, dirs, files in os.walk(self.root_dir):
            rel_root = os.path.relpath(root, self.root_dir).replace("\\", "/")
            
            # Filtro de diretórios ignorados
            dirs[:] = [
                d for d in dirs 
                if d not in self.ignored_dirs and not any(rel_root.startswith(i) for i in self.ignored_dirs)
            ]

            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, self.root_dir).replace("\\", "/")

                if file.endswith(".php"):
                    inventory["all_php"].append(full_path)
                    
                    if "routes/" in rel_path or "Routes/" in rel_path:
                        inventory["routes"].append(full_path)
                    elif "Controllers/" in rel_path or "Controller.php" in file:
                        inventory["controllers"].append(full_path)
                    elif "Requests/" in rel_path or "Request.php" in file:
                        inventory["requests"].append(full_path)
                    elif "Models/" in rel_path or "Entities/" in rel_path or "Contracts/" in rel_path:
                        inventory["models"].append(full_path)
                    elif "Repositories/" in rel_path or "Repository.php" in file:
                        inventory["repositories"].append(full_path)
                    elif "Services/" in rel_path or "Service.php" in file:
                        inventory["services"].append(full_path)
                    elif "Middleware/" in rel_path:
                        inventory["middleware"].append(full_path)

                elif file.endswith((".js", ".vue", ".blade.php", ".ts")):
                    if any(p in rel_path for p in ["resources/", "packages/", "modules/"]):
                        inventory["frontend"].append(full_path)

        return inventory
