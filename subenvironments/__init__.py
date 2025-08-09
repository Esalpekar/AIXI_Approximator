"""Subenvironments package for LLM-AIXI project."""

from .file_system import process_file_system_action, FILE_SYSTEM_DOCS
from .web_search import process_web_search_action, WEB_SEARCH_DOCS
from .code_executor import process_code_execution_action, CODE_EXECUTOR_DOCS
from .consultant import process_consultant_action, CONSULTANT_DOCS

# Registry of all available subenvironments
SUBENVIRONMENTS = {
    "file_system": {
        "function": process_file_system_action,
        "docs": FILE_SYSTEM_DOCS,
        "description": "Safe file operations within Working Directory"
    },
    "web_search": {
        "function": process_web_search_action,
        "docs": WEB_SEARCH_DOCS,
        "description": "Web search using DuckDuckGo API"
    },
    "code_executor": {
        "function": process_code_execution_action,
        "docs": CODE_EXECUTOR_DOCS,
        "description": "Safe Python code execution with security restrictions"
    },
    "consultant": {
        "function": process_consultant_action,
        "docs": CONSULTANT_DOCS,
        "description": "LLM consultation for second opinions and brainstorming"
    }
}

def get_all_docs() -> str:
    """
    Get documentation for all subenvironments.
    
    Returns:
        Combined documentation string
    """
    docs = ["AVAILABLE SUBENVIRONMENTS", "=" * 50, ""]
    
    for name, info in SUBENVIRONMENTS.items():
        docs.append(f"SUBENVIRONMENT: {name.upper()}")
        docs.append(f"Description: {info['description']}")
        docs.append("")
        docs.append(info['docs'])
        docs.append("\n" + "=" * 50 + "\n")
    
    return "\n".join(docs)

__all__ = [
    "SUBENVIRONMENTS",
    "get_all_docs",
    "process_file_system_action",
    "process_web_search_action", 
    "process_code_execution_action",
    "process_consultant_action",
    "FILE_SYSTEM_DOCS",
    "WEB_SEARCH_DOCS",
    "CODE_EXECUTOR_DOCS",
    "CONSULTANT_DOCS"
]
