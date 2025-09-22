from itertools import islice
import json
import os
import pandas as pd
from utils import combine_sample_data, str2py, extract_code_model, TokenManager
from method import or_thought_modeling, debug,  or_thought_modeling_wo_understanding, or_thought_modeling_build_simplified, or_thought_modeling_understanding_simplified, zero_shot_cot, self_consistency_vote, standard
from analyze import execute_matching_files, compare_results
from utils import execute_str_function, token_cost_calculate, extract_target_text
from prompt import standard_prompt, feedback_prompt, reflection_prompt
import time

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn, track
from typing import Optional, Tuple

class Dataset:
    """ 
    This is a dataset for optimization problems.
    """

    def __init__(self,
                 dataset_name: str,
                 dataset_root: str = 'datasets/summary/',
                 item_range: Optional[Tuple[int, int]] = None,
                 problems: list = []):
        self.data_path = f'{dataset_root}/summary_{dataset_name}.json'
        with open(self.data_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        if not item_range:
            self.data = data
        else:
            self.data = dict(list(data.items())[item_range[0]:item_range[1]])
        if problems:
            self.data = {key: value for key, value in self.data.items() if key in problems}
        if dataset_name == "complexor":
            self.ground_truth = {
                key: value.get('sample')[0].get('output')[0]
                for key, value in self.data.items()
            }
        else:
            self.ground_truth = {
                key: value.get('ground_truth')
                for key, value in self.data.items()
            }
        self.prob_type = {
            key: value.get('problem_type')
            for key, value in self.data.items()}
        self.prob_size = {
            key: value.get('problem_size')
            for key, value in self.data.items()}
        self.keys = list(self.data.keys())
        
        self.if_sample_data = True if dataset_name == "complexor" else False
        # self.if_sample_data = False
        self.dataset_name = dataset_name

    def __len__(self):
        return len(self.data)



class ORThoughtModelAgent():
    """
    Answer the optimization question with solution path 
    """

    def __call__(
        self,
        dataset: Dataset,
        save_path: str,
        item_num: int,
        llm_model: str = "gpt-4.1-nano",
        temperature: float = 0.0,
        mode: str ="formalized" 
    ):

        data = dataset.data
        item_num = min(item_num, len(dataset))

        console = Console()
        """Modeling (solution path, model and code generation) Process"""

        # Initialize token manager
        token_manager = TokenManager(llm_model)

        result_path = os.path.join(save_path, f"orthought_{mode}")
        os.makedirs(result_path, exist_ok=True)
        console.print(f"result_path: {result_path}", style="bold green")
        results_file = os.path.join(result_path, f"results.json")
        result_dict = {}
        execute_results = {}
        except_keys = []

        # Use list unpacking to take the first item_num elements
        data_items = list(islice(data.items(), item_num))
        for key, value in track(
                data_items,
                description=
                f"🦊 | ORThought Model Agent ({mode})| Processing -{dataset.dataset_name}-..."
        ):

            time.sleep(1)
            result_dict[key] = {}
            nlp = value.get('description')
            if dataset.if_sample_data:
                sample_data = value.get('sample')[0].get('input')
                nlp = combine_sample_data(nlp, sample_data)

            try:
                if mode=="formalized":
                    response, response_token_usage = or_thought_modeling(nlp=nlp, llm_model=llm_model, temperature=temperature)
                elif mode=="formalized_understanding_simplified":
                    response, response_token_usage = or_thought_modeling_understanding_simplified(nlp=nlp, llm_model=llm_model, temperature=temperature)
                elif mode=="wo_understanding":
                    response, response_token_usage = or_thought_modeling_wo_understanding(nlp=nlp, llm_model=llm_model, temperature=temperature)
                elif mode=="formalized_build_simplified":
                    response, response_token_usage = or_thought_modeling_build_simplified(nlp=nlp, llm_model=llm_model, temperature=temperature)
                else:
                    raise ValueError(f"Unknown mode: {mode}. Supported modes are: formalized, informalized, wo_understanding, wo_build, self_plan")
            except Exception as e:
                console.print(f"Error processing {key}: {e}",
                                style="bold red")
                result_dict[key]["error"] = str(e)
                except_keys.append(key)
                continue
            from utils import extract_target_text
            solution_path = extract_target_text(response, "solution_path")
            model_text, code_text = extract_code_model(response)
            result_dict[key]["solution_path"] = solution_path
            result_dict[key]["model_text"] = model_text
            result_dict[key]["code_text"] = code_text
            result_dict[key]["response"] = response

            if os.path.exists(results_file):
                with open(results_file, "r", encoding="utf-8") as file:
                    existing_data = json.load(file)
            else:
                existing_data = {}

            # combine new data
            existing_data.update(result_dict)
            # write back to file
            with open(results_file, "w", encoding="utf-8") as file:
                json.dump(existing_data,
                            file,
                            indent=2,
                            ensure_ascii=False)

            # save model and code files
            txt_filename = os.path.join(result_path, f"{key}.txt")
            with open(txt_filename, "w", encoding="utf-8") as f:
                f.write(model_text)
            py_filename = os.path.join(result_path, f"{key}.py")
            success = str2py(code_text, py_filename)
            if not success:
                console.print(f"Failed to write code for key: {key}",
                                style="bold red")

            # Add token usage to manager
            token_manager.add_usage(response_token_usage)

        console.print(f"All model and code files saved in {result_path} directory")
        console.print(f"Except keys: {except_keys}", style="bold red")
        # Show the results (Table)
        console.print(
            f"Modeling Process Completed: {len(data_items)} items processed"
        )
        token_manager.print_summary(console, style="bold green")

        token_save_path = os.path.join(result_path, "token.json")
        # Load existing data if exists and save updated data
        token_manager.load_existing_data(token_save_path)
        token_manager.save_to_file(token_save_path)


class ORThoughtSolveAgent():
    """
    Execute code, debug if needed, and compare results with ground truth.
    This agent is responsible for the solving part of the ORThought workflow.
    """

    def __call__(
        self,
        dataset: Dataset,
        save_path: str,
        item_num: int,
        base_pattern: str,
        llm_model: str = "gpt-4.1-nano",
        temperature: float = 0.0,
        debug_max_try: int = 0,
    ):

        data = dataset.data
        item_num = min(item_num, len(dataset))

        console = Console()
        """Code Execution and Debugging Process"""

        # Initialize token manager
        token_manager = TokenManager(llm_model)

        initial_path = os.path.join(save_path, base_pattern)
        if debug_max_try > 0:
            result_path = os.path.join(save_path, base_pattern, "debug")
            process_name = f"{base_pattern} Code Debugging"
        else:
            result_path = initial_path
            process_name = f"{base_pattern} Code Execution"
        
        os.makedirs(result_path, exist_ok=True)
        console.print(Panel.fit(process_name), style="bold blue")
        console.print(f"result_path: {result_path}", style="bold green")
        results_file = os.path.join(result_path, f"results.json")
        result_dict = {}
        execute_results = {}
        except_keys = []

        # Use list unpacking to take the first item_num elements
        data_items = list(islice(data.items(), item_num))
        for key, value in track(
                data_items,
                description=
                f"🦊 |{base_pattern} Debugging| Processing ({dataset.dataset_name})..."
        ):

            time.sleep(1)
            nlp = value.get('description')
            if dataset.if_sample_data:
                sample_data = value.get('sample')[0].get('input')
                nlp = combine_sample_data(nlp, sample_data)
            result_dict[key] = {}

            try:
                model_path = os.path.join(initial_path, f"{key}.txt")
                with open(model_path, 'r', encoding='utf-8') as f:
                    model_text = f.read()
            except FileNotFoundError:
                console.print(f"Model file not found for {key}. Skipping.", style="bold red")
                except_keys.append(key)
                result_dict[key]["error"] = "Model file not found"
                continue
            try:
                code_path = os.path.join(initial_path, f"{key}.py")
                with open(code_path, 'r', encoding='utf-8') as f:
                    code_text = f.read()
            except FileNotFoundError:
                console.print(f"Code file not found for {key}. Skipping.", style="bold red")
                except_keys.append(key)
                result_dict[key]["error"] = "Code file not found"
                continue

            execute_result = execute_str_function(code_text)

            debug_round = 0
            completion_tokens, prompt_tokens = 0, 0
            while (
                    type(execute_result) is str
            ) and "Error" in execute_result and debug_round < debug_max_try:
                debug_round += 1
                try:
                    response, response_token_usage = debug(
                        nlp=nlp,
                        model_text=model_text,
                        code_text=code_text,
                        error_message=execute_result,
                        llm_model=llm_model,
                        temperature=temperature
                    )
                    completion_tokens += getattr(response_token_usage, 'completion_tokens', 0)  # type: ignore
                    prompt_tokens += getattr(response_token_usage, 'prompt_tokens', 0)  # type: ignore
                except Exception as e:
                    console.print(f"Error processing {key}: {e}", style="bold red")
                    result_dict[key]["error"] = str(e)
                    except_keys.append(key)
                    continue
                code_text = extract_target_text(response, "code")
                execute_result = execute_str_function(code_text)
                result_dict[key][f"debug_round_{debug_round}"] = response
            result_dict[key]["code_text"] = code_text
            execute_results[key] = execute_result
            result_dict[key]["execute_result"] = execute_result

            if os.path.exists(results_file):
                with open(results_file, "r", encoding="utf-8") as file:
                    existing_data = json.load(file)
            else:
                existing_data = {}

            # Merge new data
            existing_data.update(result_dict)
            # Write back to file
            with open(results_file, "w", encoding="utf-8") as file:
                json.dump(existing_data, file, indent=2, ensure_ascii=False)

            # Save code file
            py_filename = os.path.join(result_path, f"{key}.py")
            success = str2py(code_text, py_filename)
            if not success:
                console.print(f"Failed to write code for key: {key}",
                              style="bold red")

            # Add token usage to manager
            token_manager.add_raw_tokens(completion_tokens, prompt_tokens)

        # comapre execute results with ground truth
        # execute_results = execute_matching_files(result_path, "*.py")
        console.print("🐻 Comparing execute results with ground truth...")
        compare_results(execute_results,
                        dataset.ground_truth,
                        result_path,
                        "code-gt-comparison_results.json",
                        is_ground_truth=True,
                        prob_type=dataset.prob_type,
                        prob_size=dataset.prob_size)
        console.print(f"👌 All results saved in {result_path} directory")
        console.print(f"Except keys: {except_keys}", style="bold red")
        console.print(
            f"{base_pattern} Debugging Process Completed: {len(data_items)} items processed"
        )
        token_manager.print_summary(console, style="bold green")

        token_save_path = os.path.join(result_path, "token.json")
        # Load existing data if exists and save updated data
        token_manager.load_existing_data(token_save_path)
        token_manager.save_to_file(token_save_path)


class Baselines():

    def __init__(self):
        self.code_result = {}
        self.pattern = ""

    def __call__(self, dataset: Dataset, save_path: str, item_num: int, pattern: str, llm_model: str = "gpt-4.1-nano", temperature: float = 0.0):

        console = Console()
        data = dataset.data
        item_num = min(item_num, len(dataset))
        result_path = os.path.join(save_path, pattern)
        os.makedirs(result_path, exist_ok=True)
        results_file = os.path.join(result_path, "results.json")
        result_dict = {}
        
        # Initialize TokenManager
        token_manager = TokenManager(llm_model)

        with Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.0f}%",
            "•",
            TextColumn("[bold green]{task.completed}/{task.total}"), 
            "•",
            TimeElapsedColumn(),
            "•",
            TimeRemainingColumn(),
            console=Console(),
            expand=True
        ) as progress:
            task = progress.add_task(f"Baseline -{pattern}- Processing data", total=item_num)

            for i, (key, value) in enumerate(islice(data.items(), item_num)):
                try:
                    import time
                    time.sleep(1)
                    problem_description = value.get('description')
                    nlp = problem_description
                    if dataset.if_sample_data:
                        sample_data = value.get('sample')[0].get('input')
                        nlp = combine_sample_data(problem_description, sample_data)

                    if pattern == "standard":
                        response, tokens = standard(nlp,
                                                    llm_model=llm_model, 
                                                    temperature=temperature)
                        model_text, code_text = extract_code_model(response)
                    elif pattern == "zero-shot_cot":
                        response, tokens = zero_shot_cot(nlp=nlp,
                                                         llm_model=llm_model,
                                                         temperature=temperature)
                        model_text, code_text = extract_code_model(response)
                    elif pattern == "self_consistency":
                        most_frequent_response, response, tokens = self_consistency_vote(nlp=nlp, 
                                                                                         llm_model=llm_model, 
                                                                                         temperature=temperature)
                        model_text, code_text = extract_code_model(most_frequent_response)
                    else:
                        console.print(f"Unknown pattern: {pattern}", style="blod red")
                        raise ValueError(f"Unknown pattern: {pattern}")

                    # Add token usage to manager
                    token_manager.add_usage(tokens)
                    
                    result_dict[key] = response
                    # Check if file exists
                    if os.path.exists(results_file):
                        with open(results_file, "r", encoding="utf-8") as file:
                            existing_data = json.load(file)
                    else:
                        existing_data = {}

                    # Merge new data
                    existing_data.update(result_dict)

                    # Write back to file
                    with open(results_file, "w", encoding="utf-8") as file:
                        json.dump(existing_data, file, indent=2, ensure_ascii=False)

                    txt_filename = os.path.join(result_path, f"{key}.txt")
                    with open(txt_filename, "w", encoding="utf-8") as f:
                        f.write(model_text)

                    py_filename = os.path.join(result_path, f"{key}.py")
                    # str2py func saves the code to .py file
                    success = str2py(code_text, py_filename)
                    if not success:
                        console.print(f"Failed to write code for key: {key}", style="bold red")
                    progress.update(task, advance=1)
                except Exception as e:
                    console.print(f"Error processing {key}: {e}", style="bold red")
                    progress.update(task, advance=1)
                    continue


        console.print("\n👌 All the problems have been translated to models and codes", style="bold green")
        console.print("-"*20)
        token_manager.print_summary(console, style="bold green")
        console.print("-"*20)
        
        token_save_path = os.path.join(result_path, "token.json")
        # Load existing data if exists and save updated data
        token_manager.load_existing_data(token_save_path)
        token_manager.save_to_file(token_save_path)
        console.print(f"👌 Token Usage is calculated and results saved in {token_save_path}\n", style="bold green")


        # Execute the code files and save the results
        console.print("🐻 Executing code generated...", style="bold green")
        execution_results = execute_matching_files(result_path, "*.py", True)
        self.code_result = execution_results
        compare_results(execution_results,
                        dataset.ground_truth,
                        result_path,
                        "code-gt-comparison_results.json",
                        is_ground_truth=True,
                        prob_type=dataset.prob_type,
                        prob_size=dataset.prob_size)
        console.print(
            f"👌 All code files have been executed and results saved in {result_path} directory", style="bold green"
        )

        console.print("Execution completed successfully.", style="bold blue")

class Reflexion():

    def __call__(
        self,
        dataset: Dataset,
        save_path: str,
        item_num: int,
        pattern: str = "standard",
        llm_model: str = "gpt-4.1-nano",
        temperature: float = 0.0,
        round_num: int = 1,
        start_round: int = 0
    ):
        from method import reflexion
        data = dataset.data
        initial_pattern = pattern
        item_num = min(item_num, len(dataset))
        initial_path = os.path.join(save_path, initial_pattern)
        console = Console()
        """Reflexion Process"""
        for r in range(start_round + 1, start_round + round_num + 1):
            # Initialize TokenManager
            token_manager = TokenManager(llm_model)

            result_path = os.path.join(save_path, "reflexion",
                                    f"round_{r}")
            console.print(
                Panel.fit(f"        Reflection -Round {r}        "),
                style="bold blue")
            os.makedirs(result_path, exist_ok=True)

            results_file = os.path.join(result_path, f"results.json")
            result_dict = {}
            execute_results = {}
            except_keys = []

            data_items = list(islice(data.items(), item_num))
            for key, value in track(
                    data_items,
                    description=
                    f"|Reflexion| Processing -{dataset.dataset_name}- Round {r}..."
            ):
                time.sleep(2)

                # A list to store history messages
                messages = []
                result_dict[key] = {}
                nlp = value.get('description')
                if dataset.if_sample_data:
                    sample_data = value.get('sample')[0].get('input')
                    nlp = combine_sample_data(nlp, sample_data)
                messages.append({"role": "user", "content": standard_prompt.format(nlp)})

                # Initialize default path
                round_result_folder_path = initial_path
                
                for i in range(r):
                    # Load the previous round's messages
                    try:
                        if i == 0:
                            round_result_file_path = os.path.join(initial_path, f"results.json")
                            round_result_folder_path = initial_path
                            df = pd.read_json(round_result_file_path,
                                            orient='index')
                            messages.append({"role": "assistant", "content": df.loc[key].values[0]})
                        else:
                            round_result_file_path = os.path.join(save_path, "reflexion", f"round_{i}", f"results.json")
                            round_result_folder_path = os.path.join(save_path, "reflexion", f"round_{i}")
                            df = pd.read_json(round_result_file_path, orient='index')
                            messages.append({"role": "user", "content": feedback_prompt})
                            messages.append({"role": "assistant", "content": df.loc[key]["feedback_response"]})
                            messages.append({"role": "user", "content": reflection_prompt})
                            messages.append({"role": "assistant", "content": df.loc[key]["reflection_response"]})
                    except:
                        console.print(f"Round {i} results not found for {key}. Skipping.",
                                      style="bold red")
                        continue

                try:
                    code_path = os.path.join(round_result_folder_path, f"{key}.py")
                    with open(code_path, 'r', encoding='utf-8') as f:
                        code_text = f.read()
                    execute_result = execute_str_function(code_text)

                except FileNotFoundError:
                    console.print(f"Code file not found for {key}. Skipping.",
                                  style="bold red")
                    execute_result = "Error: Code not found"
                    # continue
                if type(execute_result) is str and "Error" in execute_result:
                    error_message = execute_result
                else:
                    error_message = ""  # Use empty string instead of None

                try:
                    feedback_response, reflection_response, reflection_token_usage = reflexion(messages=messages, llm_model=llm_model, temperature=temperature, error_message=error_message)
                except Exception as e:
                    console.print(f"Error processing {key}: {e}",
                                  style="bold red")
                    result_dict[key]["error"] = str(e)
                    except_keys.append(key)
                    continue
                result_dict[key]["feedback_response"] = feedback_response
                result_dict[key]["reflection_response"] = reflection_response
                model_text, code_text = extract_code_model(reflection_response)
                execute_result = execute_str_function(code_text)
                execute_results[key] = execute_result

                if os.path.exists(results_file):
                    with open(results_file, "r", encoding="utf-8") as file:
                        existing_data = json.load(file)
                else:
                    existing_data = {}

                # Merge new data
                existing_data.update(result_dict)
                # Write back to file
                with open(results_file, "w", encoding="utf-8") as file:
                    json.dump(existing_data,
                              file,
                              indent=2,
                              ensure_ascii=False)

                # Save model and code files
                txt_filename = os.path.join(result_path, f"{key}.txt")
                with open(txt_filename, "w", encoding="utf-8") as f:
                    f.write(model_text)
                py_filename = os.path.join(result_path, f"{key}.py")
                success = str2py(code_text, py_filename)
                if not success:
                    console.print(f"Failed to write code for key: {key}",
                                  style="bold red")

                # Add token usage to manager
                token_manager.add_usage(reflection_token_usage)

            # compare execute results with ground truth
            console.print("🐻 Comparing execute results with ground truth...")
            compare_results(execute_results,
                            dataset.ground_truth,
                            result_path,
                            "code-gt-comparison_results.json",
                            is_ground_truth=True,
                            prob_type=dataset.prob_type,
                            prob_size=dataset.prob_size)
            console.print(f"👌 All results saved in {result_path} directory",
                          style="bold green")
            console.print(f"Except keys: {except_keys}", style="bold red")
            # Show the results (Table)
            console.print(
                f"Round {r} Self Reflection Completed: {len(data_items)} items processed",
                style="bold blue")
            token_manager.print_summary(console, style="bold green")

            token_save_path = os.path.join(result_path, "token.json")
            # Load existing data if exists and save updated data
            token_manager.load_existing_data(token_save_path)
            token_manager.save_to_file(token_save_path)
