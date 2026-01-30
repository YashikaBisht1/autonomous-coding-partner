"""
AST Parser Utility - Programmatically extracts code structure
"""
import ast
import logging
from typing import List, Dict, Set

logger = logging.getLogger(__name__)

class CodeParser:
    """Parses source code using AST to extract dependencies and structure"""
    
    @staticmethod
    def get_python_dependencies(content: str) -> List[str]:
        """Extract import dependencies from Python code"""
        try:
            tree = ast.parse(content)
            deps = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        deps.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        deps.append(node.module)
            return list(set(deps))
        except Exception as e:
            logger.error(f"AST parsing error: {e}")
            return []

    @staticmethod
    def get_structure_summary(content: str) -> Dict[str, List[str]]:
        """Extract classes and functions from Python code"""
        try:
            tree = ast.parse(content)
            summary = {"classes": [], "functions": []}
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    summary["classes"].append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    # Only top-level functions or methods for now
                    summary["functions"].append(node.name)
            return summary
        except Exception as e:
            logger.error(f"AST summary error: {e}")
            return {"classes": [], "functions": []}

code_parser = CodeParser()
