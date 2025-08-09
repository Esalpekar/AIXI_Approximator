"""
File System Subenvironment for LLM-AIXI project.
Provides safe file operations restricted to the Working Directory.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any


class FileSystemSubenvironment:
    """
    File system operations restricted to a working directory for safety.
    All file paths are relative to the working directory.
    """
    
    def __init__(self, working_directory: str = "Working Directory"):
        """
        Initialize the file system subenvironment.
        
        Args:
            working_directory: Path to the working directory (relative to project root)
        """
        self.working_directory = Path(working_directory).resolve()
        # Ensure working directory exists
        self.working_directory.mkdir(exist_ok=True)
    
    def _safe_path(self, path: str) -> Path:
        """
        Convert a relative path to a safe absolute path within working directory.
        
        Args:
            path: Relative path string
            
        Returns:
            Safe absolute path
            
        Raises:
            ValueError: If path tries to escape working directory
        """
        # Convert to Path and resolve
        requested_path = (self.working_directory / path).resolve()
        
        # Ensure the path is within working directory
        try:
            requested_path.relative_to(self.working_directory)
        except ValueError:
            raise ValueError(f"Path '{path}' is outside working directory")
        
        return requested_path
    
    def read_file(self, path: str) -> str:
        """
        Read contents of a file.
        
        Args:
            path: Relative path to file within working directory
            
        Returns:
            File contents as string, or error message
        """
        try:
            safe_path = self._safe_path(path)
            
            if not safe_path.exists():
                return f"ERROR: File '{path}' does not exist"
            
            if not safe_path.is_file():
                return f"ERROR: '{path}' is not a file"
            
            with open(safe_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return f"SUCCESS: Read file '{path}'\n\nContent:\n{content}"
            
        except Exception as e:
            return f"ERROR: Failed to read file '{path}': {str(e)}"
    
    def write_file(self, path: str, content: str) -> str:
        """
        Write content to a file.
        
        Args:
            path: Relative path to file within working directory
            content: Content to write
            
        Returns:
            Success or error message
        """
        try:
            safe_path = self._safe_path(path)
            
            # Create parent directories if they don't exist
            safe_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(safe_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"SUCCESS: Wrote {len(content)} characters to file '{path}'"
            
        except Exception as e:
            return f"ERROR: Failed to write file '{path}': {str(e)}"
    
    def list_files(self, path: str = ".") -> str:
        """
        List files and directories in a path.
        
        Args:
            path: Relative path to directory within working directory (default: current)
            
        Returns:
            Formatted list of files and directories, or error message
        """
        try:
            safe_path = self._safe_path(path)
            
            if not safe_path.exists():
                return f"ERROR: Directory '{path}' does not exist"
            
            if not safe_path.is_dir():
                return f"ERROR: '{path}' is not a directory"
            
            items = []
            for item in sorted(safe_path.iterdir()):
                relative_path = item.relative_to(self.working_directory)
                if item.is_dir():
                    items.append(f"[DIR]  {relative_path}/")
                else:
                    size = item.stat().st_size
                    items.append(f"[FILE] {relative_path} ({size} bytes)")
            
            if not items:
                return f"SUCCESS: Directory '{path}' is empty"
            
            return f"SUCCESS: Contents of directory '{path}':\n" + "\n".join(items)
            
        except Exception as e:
            return f"ERROR: Failed to list directory '{path}': {str(e)}"
    
    def file_exists(self, path: str) -> str:
        """
        Check if a file exists.
        
        Args:
            path: Relative path to file within working directory
            
        Returns:
            Existence status message
        """
        try:
            safe_path = self._safe_path(path)
            
            if safe_path.exists():
                if safe_path.is_file():
                    size = safe_path.stat().st_size
                    return f"SUCCESS: File '{path}' exists ({size} bytes)"
                elif safe_path.is_dir():
                    return f"SUCCESS: Directory '{path}' exists"
                else:
                    return f"SUCCESS: Path '{path}' exists but is neither file nor directory"
            else:
                return f"SUCCESS: Path '{path}' does not exist"
                
        except Exception as e:
            return f"ERROR: Failed to check path '{path}': {str(e)}"
    
    def delete_file(self, path: str) -> str:
        """
        Delete a file.
        
        Args:
            path: Relative path to file within working directory
            
        Returns:
            Success or error message
        """
        try:
            safe_path = self._safe_path(path)
            
            if not safe_path.exists():
                return f"ERROR: File '{path}' does not exist"
            
            if not safe_path.is_file():
                return f"ERROR: '{path}' is not a file"
            
            safe_path.unlink()
            return f"SUCCESS: Deleted file '{path}'"
            
        except Exception as e:
            return f"ERROR: Failed to delete file '{path}': {str(e)}"


# Main interface function for the orchestrator
def process_file_system_action(input_body: str) -> str:
    """
    Process a file system action from the agent.
    
    Expected input format (JSON):
    {
        "action": "read_file" | "write_file" | "list_files" | "file_exists" | "delete_file",
        "path": "relative/path/to/file",
        "content": "content for write_file action (optional)"
    }
    
    Args:
        input_body: JSON string with action details
        
    Returns:
        Result string from the file operation
    """
    fs = FileSystemSubenvironment()
    
    try:
        # Parse the input
        data = json.loads(input_body)
        action = data.get("action")
        path = data.get("path", "")
        content = data.get("content", "")
        
        if action == "read_file":
            return fs.read_file(path)
        elif action == "write_file":
            if not content:
                return "ERROR: 'content' field is required for write_file action"
            return fs.write_file(path, content)
        elif action == "list_files":
            return fs.list_files(path)
        elif action == "file_exists":
            return fs.file_exists(path)
        elif action == "delete_file":
            return fs.delete_file(path)
        else:
            return f"ERROR: Unknown action '{action}'. Available actions: read_file, write_file, list_files, file_exists, delete_file"
    
    except json.JSONDecodeError as e:
        return f"ERROR: Invalid JSON input: {str(e)}"
    except Exception as e:
        return f"ERROR: File system operation failed: {str(e)}"


# Documentation for the agent
FILE_SYSTEM_DOCS = """
FILE SYSTEM SUBENVIRONMENT

This subenvironment provides safe file operations within the Working Directory.

INPUT FORMAT (JSON):
{
    "action": "read_file" | "write_file" | "list_files" | "file_exists" | "delete_file",
    "path": "relative/path/to/file",
    "content": "content for write_file (optional)"
}

ACTIONS:
- read_file: Read contents of a file
- write_file: Write content to a file (creates directories as needed)
- list_files: List contents of a directory
- file_exists: Check if a file or directory exists
- delete_file: Delete a file

EXAMPLES:
{"action": "list_files", "path": "."}
{"action": "read_file", "path": "example.txt"}
{"action": "write_file", "path": "output.txt", "content": "Hello, world!"}
{"action": "file_exists", "path": "data.json"}
{"action": "delete_file", "path": "temp.txt"}

All paths are relative to the Working Directory for security.
"""
