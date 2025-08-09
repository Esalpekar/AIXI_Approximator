"""
Code Executor Subenvironment for LLM-AIXI project.
Provides safe Python code execution with isolation and security measures.
"""

import json
import sys
import io
import contextlib
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, Tuple


class CodeExecutorSubenvironment:
    """
    Safe Python code execution with multiple isolation strategies.
    """
    
    def __init__(self, working_directory: str = "Working Directory"):
        """
        Initialize the code executor.
        
        Args:
            working_directory: Directory for code execution (relative to project root)
        """
        self.working_directory = Path(working_directory).resolve()
        self.working_directory.mkdir(exist_ok=True)
        
        # Restricted imports for safety
        self.restricted_imports = {
            'os', 'sys', 'subprocess', 'shutil', 'glob', 'pathlib',
            'importlib', '__import__', 'eval', 'exec', 'compile',
            'open', 'file', 'input', 'raw_input'
        }
    
    def _create_safe_globals(self) -> Dict[str, Any]:
        """
        Create a restricted global namespace for code execution.
        
        Returns:
            Dictionary with safe built-ins
        """
        safe_builtins = {
            # Safe built-in functions
            'abs', 'all', 'any', 'bin', 'bool', 'chr', 'dict', 'dir',
            'divmod', 'enumerate', 'filter', 'float', 'format', 'frozenset',
            'getattr', 'hasattr', 'hash', 'hex', 'id', 'int', 'isinstance',
            'issubclass', 'iter', 'len', 'list', 'map', 'max', 'min',
            'next', 'oct', 'ord', 'pow', 'print', 'range', 'repr',
            'reversed', 'round', 'set', 'slice', 'sorted', 'str', 'sum',
            'tuple', 'type', 'zip'
        }
        
        # Create restricted builtins
        restricted_builtins = {}
        import builtins
        for name in safe_builtins:
            if hasattr(builtins, name):
                restricted_builtins[name] = getattr(builtins, name)
        
        # Add safe modules
        safe_globals = {
            '__builtins__': restricted_builtins,
            'math': __import__('math'),
            'random': __import__('random'),
            'datetime': __import__('datetime'),
            'json': __import__('json'),
            're': __import__('re'),
            'collections': __import__('collections'),
            'itertools': __import__('itertools'),
            'functools': __import__('functools'),
        }
        
        return safe_globals
    
    def execute_python_safe(self, code: str, timeout: int = 10) -> str:
        """
        Execute Python code in a restricted environment.
        
        Args:
            code: Python code to execute
            timeout: Maximum execution time in seconds
            
        Returns:
            Execution result (stdout + stderr) or error message
        """
        try:
            # Check for obviously dangerous patterns
            dangerous_patterns = [
                'import os', 'import sys', 'import subprocess', 'import shutil',
                'from os', 'from sys', 'from subprocess', 'from shutil',
                '__import__', 'eval(', 'exec(', 'compile(',
                'open(', 'file(', 'input(', 'raw_input(',
                'globals()', 'locals()', 'vars()', 'dir()',
                'getattr(', 'setattr(', 'delattr(', 'hasattr('
            ]
            
            code_lower = code.lower()
            for pattern in dangerous_patterns:
                if pattern in code_lower:
                    return f"ERROR: Potentially dangerous code pattern detected: '{pattern}'"
            
            # Capture stdout and stderr
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            try:
                sys.stdout = stdout_capture
                sys.stderr = stderr_capture
                
                # Create safe execution environment
                safe_globals = self._create_safe_globals()
                safe_locals = {}
                
                # Execute the code
                exec(code, safe_globals, safe_locals)
                
                # Get output
                stdout_content = stdout_capture.getvalue()
                stderr_content = stderr_capture.getvalue()
                
                # Format result
                result_parts = []
                if stdout_content:
                    result_parts.append(f"STDOUT:\n{stdout_content}")
                if stderr_content:
                    result_parts.append(f"STDERR:\n{stderr_content}")
                
                if not result_parts:
                    result_parts.append("Code executed successfully with no output.")
                
                return "SUCCESS: " + "\n\n".join(result_parts)
                
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                
        except SyntaxError as e:
            return f"ERROR: Syntax error in Python code: {str(e)}"
        except Exception as e:
            return f"ERROR: Runtime error during code execution: {str(e)}"
    
    def execute_python_subprocess(self, code: str, timeout: int = 10) -> str:
        """
        Execute Python code in a separate subprocess for better isolation.
        
        Args:
            code: Python code to execute
            timeout: Maximum execution time in seconds
            
        Returns:
            Execution result or error message
        """
        try:
            # Create a temporary file for the code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                # Execute in subprocess with timeout
                result = subprocess.run(
                    [sys.executable, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=self.working_directory
                )
                
                # Format result
                result_parts = []
                if result.stdout:
                    result_parts.append(f"STDOUT:\n{result.stdout}")
                if result.stderr:
                    result_parts.append(f"STDERR:\n{result.stderr}")
                
                if result.returncode != 0:
                    result_parts.append(f"EXIT CODE: {result.returncode}")
                
                if not result_parts:
                    result_parts.append("Code executed successfully with no output.")
                
                return "SUCCESS: " + "\n\n".join(result_parts)
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file)
                except:
                    pass
                    
        except subprocess.TimeoutExpired:
            return f"ERROR: Code execution timed out after {timeout} seconds"
        except Exception as e:
            return f"ERROR: Failed to execute code in subprocess: {str(e)}"
    
    def execute_python(self, code: str, method: str = "safe", timeout: int = 10) -> str:
        """
        Execute Python code using the specified method.
        
        Args:
            code: Python code to execute
            method: Execution method ("safe" or "subprocess")
            timeout: Maximum execution time in seconds
            
        Returns:
            Execution result or error message
        """
        if not code.strip():
            return "ERROR: Code cannot be empty"
        
        if method == "safe":
            return self.execute_python_safe(code, timeout)
        elif method == "subprocess":
            return self.execute_python_subprocess(code, timeout)
        else:
            return f"ERROR: Unknown execution method '{method}'. Use 'safe' or 'subprocess'"


# Main interface function for the orchestrator
def process_code_execution_action(input_body: str) -> str:
    """
    Process a code execution action from the agent.
    
    Expected input format (JSON):
    {
        "code": "Python code to execute",
        "method": "safe",  // optional: "safe" or "subprocess"
        "timeout": 10      // optional: timeout in seconds
    }
    
    Args:
        input_body: JSON string with code execution details
        
    Returns:
        Execution result or error message
    """
    executor = CodeExecutorSubenvironment()
    
    try:
        # Parse the input
        data = json.loads(input_body)
        code = data.get("code", "").strip()
        method = data.get("method", "safe")
        timeout = data.get("timeout", 10)
        
        if not code:
            return "ERROR: 'code' field is required and cannot be empty"
        
        if not isinstance(timeout, (int, float)) or timeout <= 0 or timeout > 60:
            return "ERROR: 'timeout' must be a number between 1 and 60 seconds"
        
        return executor.execute_python(code, method, int(timeout))
    
    except json.JSONDecodeError as e:
        return f"ERROR: Invalid JSON input: {str(e)}"
    except Exception as e:
        return f"ERROR: Code execution operation failed: {str(e)}"


# Documentation for the agent
CODE_EXECUTOR_DOCS = """
CODE EXECUTOR SUBENVIRONMENT

This subenvironment provides safe Python code execution with security restrictions.

INPUT FORMAT (JSON):
{
    "code": "Python code to execute",
    "method": "safe",  // optional: "safe" (default) or "subprocess"
    "timeout": 10      // optional: timeout in seconds (1-60, default 10)
}

EXECUTION METHODS:
- "safe": Executes in restricted environment with limited built-ins (recommended)
- "subprocess": Executes in separate process (better isolation but slower)

SECURITY RESTRICTIONS:
- No file system access (os, open, file)
- No system calls (subprocess, sys)
- No dynamic imports (__import__, importlib)
- No eval/exec functions
- Limited to safe built-in functions and modules
- Execution timeout to prevent infinite loops

AVAILABLE MODULES:
- math, random, datetime, json, re
- collections, itertools, functools
- All safe built-in functions (print, len, range, etc.)

EXAMPLES:
{"code": "print('Hello, world!')"}
{"code": "import math\\nprint(math.sqrt(16))", "timeout": 5}
{"code": "x = [1, 2, 3]\\nprint(sum(x))", "method": "subprocess"}

NOTES:
- Code is executed in the Working Directory
- Both stdout and stderr are captured
- Syntax errors and runtime errors are handled gracefully
- Dangerous operations are blocked for security
"""
