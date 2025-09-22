from llm_call import qwen_call, general_call
from typing import Optional, Tuple, Any


def or_thought_modeling(nlp: Optional[str] = None,
                  llm_model: str = "gpt-4.1-nano",
                  temperature: float = 0.0) -> Tuple[str, Any]:
    from prompt import formalized_solution_path_prompt
    prompt = formalized_solution_path_prompt.format(nlp=nlp)
    return general_call(prompt, llm_model=llm_model, temperature=temperature)
    
    
def or_thought_modeling_understanding_simplified(nlp: Optional[str] = None,
                  llm_model: str = "gpt-4.1-nano",
                  temperature: float = 0.0) -> Tuple[str, Any]:
    from prompt import formalized_solution_path_understanding_simplified_prompt
    prompt = formalized_solution_path_understanding_simplified_prompt.format(nlp=nlp)
    return general_call(prompt, llm_model=llm_model, temperature=temperature)
    

def or_thought_modeling_build_simplified(nlp: Optional[str] = None,
                  llm_model: str = "gpt-4.1-nano",
                  temperature: float = 0.0) -> Tuple[str, Any]:
    from prompt import formalized_solution_path_build_simplified_prompt
    prompt = formalized_solution_path_build_simplified_prompt.format(nlp=nlp)
    return general_call(prompt, llm_model=llm_model, temperature=temperature)
    


def or_thought_modeling_wo_understanding(nlp: Optional[str] = None,
                                            llm_model: str = "gpt-4.1-nano",
                                            temperature: float = 0.0) -> Tuple[str, Any]:
    from prompt import formalized_solution_path_wo_understanding_prompt
    prompt = formalized_solution_path_wo_understanding_prompt.format(nlp=nlp)
    return general_call(prompt, llm_model=llm_model, temperature=temperature)
    

def debug(nlp: Optional[str] = None,
          model_text: Optional[str] = None,
          code_text: Optional[str] = None,
          error_message: Optional[str] = None,
          llm_model: str = "gpt-4.1-nano",
          temperature: float = 0.0) -> Tuple[str, Any]:

    from prompt import debug_prompt

    prompt = debug_prompt.format(nlp=nlp, model_text=model_text, code_text=code_text, error_message=error_message)
    response, token_usage = general_call(prompt, llm_model=llm_model, temperature=temperature)

    return response, token_usage


def zero_shot_cot(nlp, llm_model: str = "qwen3-8b", temperature: float = 0.0):
    cot_prompt = "Now, Let's think step by step."
    task = f"""
    The problem description is as follows:
    {nlp}
    
    Please provide its mathematical model and Gurobipy code to solve this problem.  The code you return should be a callable function whose parameters have default values extracted from the problem, and whose return value is the optimal objective function value of the model (if it exists), otherwise return None. Your response should include:
    
    ```model
    [Your Model]
    ```
    
    ```python
    [Your Code]
    ```
    
    {cot_prompt}
    """
    return general_call(task, temperature=temperature, llm_model=llm_model)


def self_consistency_vote(nlp: str,
                          num: int = 3,
                          llm_model: str = "gpt-4.1-nano",
                          temperature: float = 0.5):
    from utils import extract_code, execute_str_function, get_random_index_of_most_frequent
    task = f"""
    The problem description is as follows:
    {nlp}
    Please provide Gurobipy code and mathematical model to solve this problem.  The code you return should be a callable function whose parameters have default values extracted from the problem, and whose return value is the optimal objective function value of the model (if it exists), otherwise return None. 
    Your response should be this format:
    ```model
    [Your Model]
    ```
    ```python
    [Your Code]
    ```
    """
    responses = []
    tokens = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0
    }
    for _ in range(num):
        response, token_usage = general_call(task, temperature=temperature, llm_model=llm_model)
        tokens["prompt_tokens"] += token_usage.prompt_tokens
        tokens["completion_tokens"] += token_usage.completion_tokens
        tokens["total_tokens"] += token_usage.total_tokens
        responses.append(response)

    # execute the code and vote for popular result
    results = []

    for response in responses:
        try:
            clean_code = extract_code(response)
            result = execute_str_function(clean_code)
            results.append(str(result))
        except Exception as e:
            results.append(str(e))
    most_frequent_answer_index = get_random_index_of_most_frequent(results)
    most_frequent_answer = responses[most_frequent_answer_index]
    responses.append(results)

    from types import SimpleNamespace
    tokens = SimpleNamespace(**tokens)

    return most_frequent_answer, responses, tokens


def standard(nlp: str,
             llm_model: str = "gpt-4.1-nano",
             temperature: float = 0.0):

    task = f"""
    The problem description is as follows:{nlp}
    Please provide a mathematical model and Gurobipy code to solve this problem. The code you return should be a callable function whose parameters have default values extracted from the problem, and whose return value is the optimal objective function value of the model (if it exists), otherwise return None. No example for calling the function is required.
    Your response should be this format:
    ```model
    [Your Model]
    ```
    ```python
    [Your Code]
    ```
    """

    return general_call(task, temperature=temperature, llm_model=llm_model)


def reflexion(error_message: Optional[str] = None,
              messages: Optional[list] = None,
              llm_model: str = "gpt-4.1-nano",
              temperature: float = 0.0) -> Tuple[str, str, Any]:

    from prompt import feedback_prompt, reflection_prompt
    if messages is None:
        raise ValueError("Messages cannot be None.")

    self_feedback_prompt = feedback_prompt.format(error_message=str(error_message))
    messages.append({"role": "user", "content": self_feedback_prompt})
    feedback_response, token2 = general_call(messages=messages,
                                             temperature=temperature,
                                             llm_model=llm_model,
                                             )

    messages.append({"role": "assistant", "content": feedback_response})

    self_reflection_prompt = reflection_prompt

    messages.append({"role": "user", "content": self_reflection_prompt})
    reflection_response, token3 = general_call(messages=messages,
                                               temperature=temperature,
                                               llm_model=llm_model,
                                               )
    messages.append({"role": "assistant", "content": reflection_response})

    tokens = {
        "prompt_tokens": token2.prompt_tokens + token3.prompt_tokens,
        "completion_tokens": token2.completion_tokens + token3.completion_tokens,
        "total_tokens": token2.total_tokens + token3.total_tokens
    }
    from types import SimpleNamespace
    tokens = SimpleNamespace(**tokens)

    return feedback_response, reflection_response, tokens