import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from uuid import uuid4
import shutil
from playwright.sync_api import sync_playwright

class MultiLanguageCodeExecutor:
    def __init__(self, base_dir=".sandbox"):
        self.base_dir = Path(base_dir).resolve()
        self.base_dir.mkdir(exist_ok=True)

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        language = data.get("language")
        code = data.get("code")
        filename = data.get("filename")  # Optional: let user control it
        eval_js = data.get("eval_js")    # Optional for HTML

        if language not in ["python", "javascript", "html"]:
            return {"error": f"Unsupported language: {language}"}

        task_id = str(uuid4())
        task_dir = self.base_dir / task_id
        task_dir.mkdir(parents=True)

        try:
            extension = {
                "python": "py",
                "javascript": "js",
                "html": "html"
            }[language]
            filename = filename or f"main.{extension}"
            file_path = task_dir / filename
            file_path.write_text(code)

            if language == "python":
                return self._run_subprocess(["python", str(file_path)], task_dir)
            elif language == "javascript":
                return self._run_subprocess(["node", str(file_path)], task_dir)
            elif language == "html":
                return self._run_html(file_path, eval_js)
        except Exception as e:
            return {"error": str(e)}
        finally:
            shutil.rmtree(task_dir, ignore_errors=True)

    def _run_subprocess(self, command: list, cwd: Path) -> Dict[str, Any]:
        try:
            result = subprocess.run(
                command,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=10
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": "Execution timed out"}

    def _run_html(self, file_path: Path, eval_js: Optional[str]) -> Dict[str, Any]:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(f"file://{file_path.resolve()}")

                eval_result = None
                if eval_js:
                    eval_result = page.evaluate(eval_js)

                content = page.content()
                browser.close()

                return {
                    "dom": content[:5000],
                    "eval_result": eval_result
                }
        except Exception as e:
            return {"error": f"HTML evaluation failed: {str(e)}"}
        
def create_code_executor():
    """Factory function to expose the executor's interface."""
    executor = MultiLanguageCodeExecutor()
    return executor.execute