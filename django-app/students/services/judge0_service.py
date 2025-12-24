"""
Judge0 Code Execution Service

This service handles communication with the Judge0 API for code execution.
"""
import requests
import time
import base64
from typing import Dict, Any, Optional, List
from django.conf import settings


class Judge0Service:
    """
    Service for executing code via Judge0 API.
    
    Judge0 is a code execution system that supports multiple programming languages.
    """
    
    # RapidAPI Judge0 endpoint
    BASE_URL = "https://judge0-ce.p.rapidapi.com"
    
    # Language IDs for Judge0 (common ones)
    LANGUAGE_IDS = {
        'python': 71,      # Python (3.8.1)
        'python3': 71,     # Python (3.8.1)
        'javascript': 63,  # JavaScript (Node.js 12.14.0)
        'java': 62,        # Java (OpenJDK 13.0.1)
        'c': 50,           # C (GCC 9.2.0)
        'cpp': 54,         # C++ (GCC 9.2.0)
        'csharp': 51,      # C# (Mono 6.6.0.161)
        'go': 60,          # Go (1.13.5)
        'ruby': 72,        # Ruby (2.7.0)
        'rust': 73,        # Rust (1.40.0)
        'typescript': 74,  # TypeScript (3.7.4)
        'php': 68,         # PHP (7.4.1)
        'swift': 83,       # Swift (5.2.3)
        'kotlin': 78,      # Kotlin (1.3.70)
    }
    
    def __init__(self, api_key: str = None):
        """
        Initialize Judge0 service with API key.
        
        Args:
            api_key: RapidAPI key for Judge0. If not provided, uses settings.
        """
        self.api_key = api_key or getattr(settings, 'JUDGE0_API_KEY', None)
        if not self.api_key:
            raise ValueError("Judge0 API key is required")
        
        self.headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com"
        }
    
    def get_language_id(self, language: str) -> int:
        """
        Get Judge0 language ID from language name.
        
        Args:
            language: Programming language name (e.g., 'python', 'javascript')
        
        Returns:
            Language ID for Judge0
        
        Raises:
            ValueError: If language is not supported
        """
        language = language.lower().replace(' ', '')
        if language not in self.LANGUAGE_IDS:
            raise ValueError(f"Unsupported language: {language}")
        return self.LANGUAGE_IDS[language]
    
    def encode_base64(self, text: str) -> str:
        """Encode text to base64."""
        return base64.b64encode(text.encode('utf-8')).decode('utf-8')
    
    def decode_base64(self, encoded: str) -> str:
        """Decode base64 to text."""
        if not encoded:
            return ""
        try:
            return base64.b64decode(encoded).decode('utf-8')
        except Exception:
            return encoded
    
    def create_submission(
        self,
        source_code: str,
        language: str,
        stdin: str = "",
        expected_output: str = None,
        time_limit: float = 5.0,
        memory_limit: int = 128000,
        wait: bool = True
    ) -> Dict[str, Any]:
        """
        Create a code submission and execute it.
        
        Args:
            source_code: The code to execute
            language: Programming language
            stdin: Standard input for the program
            expected_output: Expected output for comparison
            time_limit: Maximum execution time in seconds
            memory_limit: Maximum memory in KB
            wait: If True, wait for completion; if False, return token
        
        Returns:
            Dictionary with execution results
        """
        try:
            language_id = self.get_language_id(language)
            
            payload = {
                "language_id": language_id,
                "source_code": self.encode_base64(source_code),
                "stdin": self.encode_base64(stdin) if stdin else "",
                "cpu_time_limit": time_limit,
                "memory_limit": memory_limit,
            }
            
            if expected_output:
                payload["expected_output"] = self.encode_base64(expected_output)
            
            # Submit the code
            url = f"{self.BASE_URL}/submissions"
            params = {"base64_encoded": "true", "wait": str(wait).lower()}
            
            response = requests.post(
                url,
                json=payload,
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 201 or response.status_code == 200:
                result = response.json()
                return self._parse_result(result)
            else:
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code}",
                    "details": response.text
                }
        
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timeout",
                "details": "The code execution request timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Execution error",
                "details": str(e)
            }
    
    def get_submission(self, token: str) -> Dict[str, Any]:
        """
        Get the result of a submission by token.
        
        Args:
            token: Submission token from create_submission
        
        Returns:
            Dictionary with execution results
        """
        try:
            url = f"{self.BASE_URL}/submissions/{token}"
            params = {"base64_encoded": "true"}
            
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return self._parse_result(result)
            else:
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code}",
                    "details": response.text
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": "Error fetching submission",
                "details": str(e)
            }
    
    def wait_for_result(self, token: str, max_wait: int = 30, interval: float = 0.5) -> Dict[str, Any]:
        """
        Poll for submission result until complete.
        
        Args:
            token: Submission token
            max_wait: Maximum seconds to wait
            interval: Polling interval in seconds
        
        Returns:
            Dictionary with execution results
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            result = self.get_submission(token)
            
            # Status ID 1 and 2 mean "In Queue" and "Processing"
            status_id = result.get('status_id', 0)
            if status_id not in [1, 2]:
                return result
            
            time.sleep(interval)
        
        return {
            "success": False,
            "error": "Timeout",
            "details": "Execution took too long"
        }
    
    def _parse_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse and decode the Judge0 API result.
        
        Args:
            result: Raw result from Judge0 API
        
        Returns:
            Parsed result dictionary
        """
        # Decode base64 fields
        stdout = self.decode_base64(result.get('stdout', ''))
        stderr = self.decode_base64(result.get('stderr', ''))
        compile_output = self.decode_base64(result.get('compile_output', ''))
        message = result.get('message', '')
        
        status = result.get('status', {})
        status_id = status.get('id', 0) if isinstance(status, dict) else result.get('status_id', 0)
        status_desc = status.get('description', '') if isinstance(status, dict) else ''
        
        # Determine if execution was successful
        # Status ID 3 = Accepted (correct output)
        # Status ID 4 = Wrong Answer
        # Other statuses indicate errors
        success = status_id == 3
        
        return {
            "success": success,
            "status_id": status_id,
            "status": status_desc,
            "stdout": stdout.strip(),
            "stderr": stderr.strip(),
            "compile_output": compile_output.strip(),
            "message": message,
            "time": result.get('time'),
            "memory": result.get('memory'),
            "token": result.get('token'),
            "exit_code": result.get('exit_code')
        }
    
    def run_test_cases(
        self,
        source_code: str,
        language: str,
        test_cases: List[Dict[str, Any]],
        time_limit: float = 5.0
    ) -> Dict[str, Any]:
        """
        Run code against multiple test cases.
        
        Args:
            source_code: The code to execute
            language: Programming language
            test_cases: List of test cases with 'input' and 'expected_output'
            time_limit: Time limit per test case
        
        Returns:
            Dictionary with overall results and individual test results
        """
        results = []
        passed = 0
        total = len(test_cases)
        
        for i, test_case in enumerate(test_cases):
            stdin = test_case.get('input', '')
            expected = test_case.get('expected_output', '')
            
            result = self.create_submission(
                source_code=source_code,
                language=language,
                stdin=stdin,
                expected_output=expected,
                time_limit=time_limit,
                wait=True
            )
            
            # Compare outputs (trim whitespace)
            actual_output = result.get('stdout', '').strip()
            expected_output = expected.strip()
            test_passed = actual_output == expected_output
            
            if test_passed:
                passed += 1
            
            results.append({
                "test_case": i + 1,
                "passed": test_passed,
                "input": stdin,
                "expected_output": expected_output,
                "actual_output": actual_output,
                "error": result.get('stderr') or result.get('compile_output') or result.get('message'),
                "time": result.get('time'),
                "memory": result.get('memory'),
                "status": result.get('status'),
                "status_id": result.get('status_id')
            })
        
        return {
            "passed": passed,
            "total": total,
            "score": round((passed / total) * 100) if total > 0 else 0,
            "all_passed": passed == total,
            "results": results
        }


# Singleton instance with lazy initialization
_judge0_service = None

def get_judge0_service(api_key: str = None) -> Judge0Service:
    """
    Get or create Judge0 service instance.
    
    Args:
        api_key: Optional API key override
    
    Returns:
        Judge0Service instance
    """
    global _judge0_service
    
    if api_key:
        return Judge0Service(api_key)
    
    if _judge0_service is None:
        _judge0_service = Judge0Service()
    
    return _judge0_service
