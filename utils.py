import os
import random
import re
from collections import Counter


def get_random_index_of_most_frequent(results: list) -> int:
    """
    Randomly get a random index of the most frequent value in `results`.

    Args:
        results (list): Input list.

    Returns:
        int: Random index of the most frequent value.
    """
    # Count the occurrences of each value
    count = Counter(results)

    # Find the values with the highest occurrence count
    max_count = max(count.values())
    most_frequent_values = [
        key for key, val in count.items() if val == max_count
    ]

    # Randomly select one of the most frequent values
    chosen_value = random.choice(most_frequent_values)

    # Find all indices corresponding to this value
    indices = [i for i, val in enumerate(results) if val == chosen_value]

    # Randomly return one index
    return random.choice(indices)


def combine_sample_data(nlp, sample_data):
    """
    Combine the natural language problem description with sample data.

    Args:
    ----------
    nlp : str
        A problem description in natural language that specifies an optimization
        problem to be solved.
        sample_data : str
        Sample data to be combined with the natural language problem description.

    Returns:
    -------
    str
        Combined string of the natural language problem description and sample data.
    """
    combine_result = f"Problem Description: {nlp}\nSample Data: {sample_data}"

    return combine_result


def extract_code(string):
    """
    Extract the code from a string representation of Python code.

    Args:
    ----------
    string : str
        A string containing Python code.

    Returns:
    -------
    str
        The extracted code from the input string.
    """
    python_start = string.find("```python")
    if python_start == -1:
        return string

    # find the start of the code block (after the "```python" line)
    code_start = string.find("\n", python_start) + 1

    # find the end of the code block (before the next "```" line)
    code_end = string.find("```\n", code_start)
    if code_end == -1:
        code_end = string.find("```", code_start)

    # extract the code block
    python_code = string[code_start:code_end].strip()
    return python_code


def extract_code_model(string):
    """
    Extract the code and model from a string representation of Python code.

    Args:
    ----------
    string : str
        A string containing Python code.

    Returns:
    -------
    model : str
        The extracted model from the input string.
    code : str
        The extracted code from the input string.
    """
    model = "No model found"
    code = "No code found"

    # Regex to find model block (```model, ```latex, ```markdown, '''model)
    model_pattern = re.compile(r"```(?:model|latex|markdown)\s*\n(.*?)\n```", re.DOTALL)
    model_match = model_pattern.search(string)
    if model_match:
        model = model_match.group(1).strip()

    # In case of ```python\n```python, we need to fix the malformed pattern
    if "```python\n```python" in string:
        # Remove the first incorrect ```python to fix the malformed pattern
        string = string.replace("```python\n```python", "```python", 1)

    # Regex to find all python code blocks and find the longest one
    code_pattern = re.compile(r"```(?:python|code)\s*\n(.*?)\n```", re.DOTALL)
    all_matches = code_pattern.findall(string)

    if all_matches:
        # Set a minimum length for the code to be considered valid
        min_length = 400
        
        # Find the longest code block that meets the minimum length requirement
        longest_code = ""
        for match in all_matches:
            if len(match.strip()) > len(longest_code):
                longest_code = match.strip()
        
        if len(longest_code) > min_length:
            code = longest_code

    # Fallback for <code>...</code> tags if no other code block was found
    if code == "No code found":
        code_html_pattern = re.compile(r"<code>\s*\n(.*?)\n</code>", re.DOTALL)
        code_html_match = code_html_pattern.search(string)
        if code_html_match:
            code = code_html_match.group(1).strip()

    return model, code


def extract_target_text(string: str, target_mark: str) -> str:
    # find the start of the target text block (after the "<target_text>" line)
    target_start = string.rfind(f"<{target_mark}>")
    if target_mark == "code" and target_start == -1:
        target_start = string.rfind("```python")
    if target_start == -1:
        return "No target text found"

    target_start = string.find("\n", target_start) + 1

    # find the end of the model block (before the next "<target_text>" line)
    target_end = string.find(f"</{target_mark}>", target_start)
    if target_mark == "code" and target_end == -1:
        target_end = string.find("```", target_start)

    # extract the model block
    target_text = string[target_start:target_end].strip()

    return target_text


def str2py(string, output_filename):
    """
    Writes a given string containing Python code to a .py file.

    Args:
    ----------
    string : str
        A string containing Python code.
    output_filename : str
        The path where the Python code will be saved as a .py file.

    Returns:
    -------
    bool
        True if writing was successful, False otherwise.
    """
    # Basic validation: Ensure the filename ends with .py (optional but recommended)
    if not output_filename.lower().endswith('.py'):
        print(
            f"Warning: Output filename '{output_filename}' does not end with .py. Adding it."
        )
        output_filename += ".py"

    # print(f"Attempting to save code string to '{output_filename}'...")

    try:
        # Ensure the directory exists if the filename includes a path
        output_dir = os.path.dirname(output_filename)
        # Check if output_dir is not empty (i.e., a path was specified)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created directory: {output_dir}")

        # Write the string content to the .py file using UTF-8 encoding
        with open(output_filename, 'w', encoding='utf-8') as outfile:
            outfile.write(string)
        # print(f"Successfully saved code to '{output_filename}'.")
        return True

    except IOError as e:
        # Handle errors specifically related to file I/O
        print(f"Error: Could not write file '{output_filename}'. Reason: {e}")
        return False
    except Exception as e:
        # Handle any other unexpected errors during the process
        print(f"An unexpected error occurred: {e}")
        return False


def execute_str_function(code_str: str):
    import tempfile
    import os
    import importlib.util

    with tempfile.TemporaryDirectory() as tmpdir:
        module_path = os.path.join(tmpdir, "temp_module.py")

        # Write code to temporary file
        with open(module_path, "w", encoding="utf-8") as f:
            f.write(code_str)

        # Load module
        spec = importlib.util.spec_from_file_location("temp_module",
                                                      module_path)
        if spec is None or spec.loader is None:
            return f"Error: Could not load module from {module_path}"
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            return format_user_traceback(e, module_path)

        # Find the first non-built-in, non-private function
        found_func = None
        for name in dir(module):
            if name.startswith('__'):
                continue
            func = getattr(module, name)
            if callable(func) and isinstance(func, type(lambda: None)):
                found_func = func
                break

        if found_func is None:
            return "Error: No callable function found in the code."

        # Call function
        try:
            return found_func()
        except Exception as e:
            return format_user_traceback(e, module_path)


def format_user_traceback(exception, user_module_path):
    import traceback
    import linecache

    tb = exception.__traceback__
    while tb:
        frame = tb.tb_frame
        filename = frame.f_code.co_filename
        if filename == user_module_path:
            lineno = tb.tb_lineno
            error_line = linecache.getline(filename, lineno).rstrip()

            context_lines = []
            for i in range(max(1, lineno - 3), lineno + 3):
                line = linecache.getline(filename, i).rstrip()
                prefix = "-->" if i == lineno else "   "
                context_lines.append(f"{prefix} {i}: {line}")

            context = '\n'.join(context_lines)
            error_msg = ''.join(
                traceback.format_exception_only(type(exception), exception))

            return (f"Error during execution:\n"
                    f"{error_msg}\n"
                    f"File \"{filename}\", line {lineno}\n"
                    f"{context}")
        tb = tb.tb_next

    full_tb = ''.join(
        traceback.format_exception(type(exception), exception,
                                   exception.__traceback__))
    return full_tb


def token_cost_calculate(token_usage: dict):
    """Legacy function for backward compatibility - use TokenManager.calculate_cost instead"""
    # Create a temporary TokenManager instance to use the cost calculation
    temp_manager = TokenManager(token_usage.get("model", "gpt-4.1-nano"))
    return temp_manager.calculate_cost(token_usage)


class TokenManager:
    """
    A centralized token usage and cost manager to simplify token calculations.
    """
    
    # Cost table as class variable - dollar for 1M tokens
    COST_TABLE = {
        "qwen3-235b-a22b": {"prompt": 0.7, "completion": 2.8},
        "qwen3-32b": {"prompt": 0.7, "completion": 2.8},
        "qwen3-14b": {"prompt": 0.35, "completion": 1.4},
        "qwen3-8b": {"prompt": 0.18, "completion": 0.7},
        "qwen3-4b": {"prompt": 0.11, "completion": 0.42},
        "qwen3-1.7b": {"prompt": 0.11, "completion": 0.42},
        "gpt-4.1-nano": {"prompt": 0.10, "completion": 0.40},
        "GPT4.1-nano": {"prompt": 0.10, "completion": 0.40},
        "GPT4.1": {"prompt": 2, "completion": 8},
        "DeepSeek-V3": {"prompt": 0.27, "completion": 1.10},
    }
    
    def __init__(self, llm_model: str):
        self.llm_model = llm_model
        self.token_usage = {
            "completion_tokens": 0,
            "prompt_tokens": 0,
            "total_tokens": 0,
            "num": 0,
            "model": llm_model
        }
        self.token_cost = {
            "completion_cost": 0,
            "prompt_cost": 0,
            "total_cost": 0,
            "completion_avg_cost": 0,
            "prompt_avg_cost": 0,
            "total_avg_cost": 0
        }
    
    def calculate_cost(self, token_usage: dict):
        """Calculate token costs based on usage"""
        use_model = token_usage["model"]
        completion_tokens = token_usage["completion_tokens"]
        prompt_tokens = token_usage["prompt_tokens"]
        completion_price = self.COST_TABLE[use_model]["completion"]
        prompt_price = self.COST_TABLE[use_model]["prompt"]

        prompt_cost = prompt_tokens * prompt_price / 1000000
        completion_cost = completion_tokens * completion_price / 1000000
        total_cost = prompt_cost + completion_cost

        return prompt_cost, completion_cost, total_cost
    
    def add_usage(self, response_token_usage):
        """Add token usage from a single response"""
        completion_tokens = getattr(response_token_usage, 'completion_tokens', 0)
        prompt_tokens = getattr(response_token_usage, 'prompt_tokens', 0)
        
        self.token_usage["completion_tokens"] += completion_tokens
        self.token_usage["prompt_tokens"] += prompt_tokens
        self.token_usage["num"] += 1
        self.token_usage["total_tokens"] = self.token_usage["completion_tokens"] + self.token_usage["prompt_tokens"]
        
        # Calculate costs
        prompt_cost, completion_cost, total_cost = self.calculate_cost(self.token_usage)
        self.token_cost["prompt_cost"] = prompt_cost
        self.token_cost["completion_cost"] = completion_cost
        self.token_cost["total_cost"] = total_cost
        
        # Calculate averages
        if self.token_usage["num"] > 0:
            self.token_cost["prompt_avg_cost"] = self.token_cost["prompt_cost"] / self.token_usage["num"]
            self.token_cost["completion_avg_cost"] = self.token_cost["completion_cost"] / self.token_usage["num"]
            self.token_cost["total_avg_cost"] = self.token_cost["total_cost"] / self.token_usage["num"]
    
    def add_raw_tokens(self, completion_tokens: int, prompt_tokens: int):
        """Add raw token counts"""
        self.token_usage["completion_tokens"] += completion_tokens
        self.token_usage["prompt_tokens"] += prompt_tokens
        self.token_usage["num"] += 1
        self.token_usage["total_tokens"] = self.token_usage["completion_tokens"] + self.token_usage["prompt_tokens"]
        
        # Calculate costs
        prompt_cost, completion_cost, total_cost = self.calculate_cost(self.token_usage)
        self.token_cost["prompt_cost"] = prompt_cost
        self.token_cost["completion_cost"] = completion_cost
        self.token_cost["total_cost"] = total_cost
        
        # Calculate averages
        if self.token_usage["num"] > 0:
            self.token_cost["prompt_avg_cost"] = self.token_cost["prompt_cost"] / self.token_usage["num"]
            self.token_cost["completion_avg_cost"] = self.token_cost["completion_cost"] / self.token_usage["num"]
            self.token_cost["total_avg_cost"] = self.token_cost["total_cost"] / self.token_usage["num"]
    
    def load_existing_data(self, token_file_path: str):
        """Load existing token data from file if it exists"""
        import json
        import os
        
        if os.path.exists(token_file_path):
            with open(token_file_path, "r", encoding="utf-8") as f:
                token_data = json.load(f)
            
            # Add existing data to current usage
            existing_usage = token_data.get("token_usage", {})
            existing_cost = token_data.get("token_cost", {})
            
            self.token_usage["prompt_tokens"] += existing_usage.get("prompt_tokens", 0)
            self.token_usage["completion_tokens"] += existing_usage.get("completion_tokens", 0)
            self.token_usage["total_tokens"] += existing_usage.get("total_tokens", 0)
            self.token_usage["num"] += existing_usage.get("num", 0)
            
            # Recalculate costs with new totals
            self.token_usage["total_tokens"] = self.token_usage["completion_tokens"] + self.token_usage["prompt_tokens"]
            
            # Calculate new costs
            prompt_cost, completion_cost, total_cost = self.calculate_cost(self.token_usage)
            self.token_cost["prompt_cost"] = prompt_cost
            self.token_cost["completion_cost"] = completion_cost
            self.token_cost["total_cost"] = total_cost
            
            # Calculate averages
            if self.token_usage["num"] > 0:
                self.token_cost["prompt_avg_cost"] = self.token_cost["prompt_cost"] / self.token_usage["num"]
                self.token_cost["completion_avg_cost"] = self.token_cost["completion_cost"] / self.token_usage["num"]
                self.token_cost["total_avg_cost"] = self.token_cost["total_cost"] / self.token_usage["num"]
    
    def save_to_file(self, token_file_path: str):
        """Save token data to file"""
        import json
        import os
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(token_file_path), exist_ok=True)
        
        token_to_save = {
            "token_usage": self.token_usage,
            "token_cost": self.token_cost
        }
        
        with open(token_file_path, "w", encoding="utf-8") as f:
            json.dump(token_to_save, f, indent=2, ensure_ascii=False)
    
    def get_usage(self):
        """Get current token usage"""
        return self.token_usage.copy()
    
    def get_cost(self):
        """Get current token cost"""
        return self.token_cost.copy()
    
    def print_summary(self, console, style="bold green"):
        """Print token usage and cost summary"""
        console.print(f"Token Usage: {self.token_usage}", style=style)
        console.print(f"Token Cost (dollar): {self.token_cost}", style=style)
