# project_root/subenvironments/file_system.py

import os
import json
from typing import Dict, Any, List
from pathlib import Path

# Specify a fixed, safe working directory here
SAFE_WORKING_DIR = Path("/users/elliottsalpekar/documents/agent_workspace/playground").resolve()

class FileSystemManager:
    """Safe file system operations within working directory"""

    def __init__(self):
        self.working_dir = SAFE_WORKING_DIR
        # Ensure the playground directory exists
        self.working_dir.mkdir(parents=True, exist_ok=True)

    def operate(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform file system operations"""

        if isinstance(operation_data, str):
            operation_data = {"operation": "list", "path": "."}

        operation = operation_data.get("operation", "list")
        path = operation_data.get("path", ".")

        try:
            full_path = (self.working_dir / path).resolve()

            if not str(full_path).startswith(str(self.working_dir)):
                return {"error": "Access denied: Path outside working directory"}

            if operation == "list":
                return self._list_directory(full_path)
            elif operation == "read":
                return self._read_file(full_path)
            elif operation == "write":
                content = operation_data.get("content", "")
                return self._write_file(full_path, content)
            elif operation == "exists":
                return self._exists(full_path)
            else:
                return {"error": f"Unknown operation: {operation}"}

        except Exception as e:
            return {"error": f"File system error: {str(e)}"}

    def _list_directory(self, path: Path) -> Dict[str, Any]:
        """List directory contents, now including the working directory."""
        if not path.is_dir():
            return {"error": "Path is not a directory"}
        items = []
        for item in path.iterdir():
            items.append({
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
            })
        return {
            "items": items,
            "path": str(path.relative_to(self.working_dir)),
            "working_directory": str(self.working_dir)
        }

    def _read_file(self, path: Path) -> Dict[str, Any]:
        """Read file contents, now including the working directory."""
        if not path.is_file():
            return {"error": "Path is not a file"}
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {
            "content": content,
            "path": str(path.relative_to(self.working_dir)),
            "working_directory": str(self.working_dir)
        }

    def _write_file(self, path: Path, content: str) -> Dict[str, Any]:
        """Write content to file, now including the working directory."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {
            "success": True,
            "bytes_written": len(content.encode('utf-8')),
            "path": str(path.relative_to(self.working_dir)),
            "working_directory": str(self.working_dir)
        }

    def _exists(self, path: Path) -> Dict[str, Any]:
        """Check if a path exists, now including the working directory."""
        return {
            "exists": path.exists(),
            "path": str(path.relative_to(self.working_dir)),
            "working_directory": str(self.working_dir)
        }


def create_file_system_manager():
    """Factory function for file system manager"""
    fs_manager = FileSystemManager()
    return fs_manager.operate