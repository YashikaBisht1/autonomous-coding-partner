"""
Analyzer Agent - Deconstructs and analyzes existing codebases
"""
import logging
from typing import Dict, Any, List
from groq_client import groq_client
from services.code_parser import code_parser

logger = logging.getLogger(__name__)

class AnalyzerAgent:
    """Agent that analyzes existing code for architecture and technical debt"""
    
    def __init__(self):
        self.system_prompt = """You are a Senior Systems Architect and Technical Auditor.
        Your goal is to analyze existing codebases to understand their architecture, 
        identify technical debt, and suggest modernization patterns.
        
        CRITICAL: Provide professional, objective, and deeply technical insights.
        Return your analysis in a structured format (JSON).
        
        Output Format:
        {
            "architecture_summary": "High-level overview of the system design",
            "components": [
                {"name": "Component Name", "purpose": "What it does", "files": ["file1", "file2"]}
            ],
            "dependencies": [
                {"source": "Component A", "target": "Component B", "type": "import/call"}
            ],
            "mermaid_graph": "A complete Mermaid.js graph string visualizing the source/target links",
            "technical_debt": [
                {"issue": "Brief description", "severity": "High/Medium/Low", "location": "file:line"}
            ],
            "refactoring_suggestions": [
                {"target": "Component/File", "suggestion": "What to change", "benefit": "Why"}
            ]
        }"""
    
    async def analyze_codebase(self, files_content: Dict[str, str], project_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a set of files to extract architectural insights
        """
        logger.info(f"Analyzing codebase for project: {project_context.get('project_name')}")
        
        # 1. Programmatic Analysis (AST)
        logical_map = {}
        for path, content in files_content.items():
            if path.endswith('.py'):
                logical_map[path] = {
                    "imports": code_parser.get_python_dependencies(content),
                    "structure": code_parser.get_structure_summary(content)
                }

        # 2. AI Reasoning
        file_summaries = []
        for path, content in files_content.items():
            snippet = content[:500] + "..." if len(content) > 500 else content
            ast_data = logical_map.get(path, "No AST available")
            file_summaries.append(f"FILE: {path}\nAST DATA: {ast_data}\nCONTENT SNIPPET:\n{snippet}\n---")
            
        consolidated_files = "\n".join(file_summaries)
        
        prompt = f"""
        PROJECT NAME: {project_context.get('project_name')}
        CONTEXT: {project_context.get('project_goal')}
        
        CODEBASE FILES:
        {consolidated_files}
        
        TASK:
        1. Deconstruct the architecture.
        2. Identify internal component dependencies using the provided AST DATA.
        3. Create a clean, colorful Mermaid.js graph string using top-down (TD) flow.
        
        CRITICAL MERMAID RULES:
        - Do NOT wrap the mermaid string in markdown code blocks (no ```mermaid).
        - Return ONLY the graph definition prompt string (e.g. "graph TD\n...").
        - Use simple alphanumeric node IDs.
        - Start with "graph TD".
        
        4. Spot technical debt (anti-patterns, security risks, lack of abstraction).
        5. Suggest modern refactoring paths.
        
        Return ONLY valid JSON.
        """
        
        try:
            analysis = await groq_client.generate_structured(
                prompt=prompt,
                system_prompt=self.system_prompt,
                json_format=True
            )
            
            # Post-process mermaid graph to be safe
            if "mermaid_graph" in analysis:
                graph = analysis["mermaid_graph"]
                # Strip markdown code blocks if present
                if graph.startswith("```mermaid"):
                    graph = graph.replace("```mermaid", "").replace("```", "")
                elif graph.startswith("```"):
                     graph = graph.replace("```", "")
                
                analysis["mermaid_graph"] = graph.strip()
                
            return analysis
        except Exception as e:
            logger.error(f"Error in codebase analysis: {e}")
            raise
