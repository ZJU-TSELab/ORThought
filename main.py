
import os
import argparse
from workflow import Dataset, Baselines, Reflexion, ORThoughtModelAgent, ORThoughtSolveAgent
from analyze import execute_matching_files, compare_results
import time
from rich.console import Console
from rich.panel import Panel


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Automated Solving of Optimization Problems Described in Natural Language')

    parser.add_argument('--dataset_name',
                        type=str,
                        nargs='+',
                        default=['logior'],
                        choices=['complexor', 'nlp4lp', 'industryor', 'logior'],
                        help='Dataset name(s) to use (default: logior)')

    parser.add_argument('--item_num',
                        type=int,
                        default=300,
                        help='Number of samples to process (default: 300)')

    parser.add_argument(
        '--item_range',
        type=int,
        nargs=2,
        help='Range of items to process as [start, end] (optional)')

    parser.add_argument(
        '--problems',
        type=str,
        nargs='+',
        default=[],
        help='List of problems to address (optional)')

    parser.add_argument('--round_mark',
                        type=int,
                        default=0,
                        help='Round number for experiments (default: 0)')

    parser.add_argument('--temperature',
                        type=float,
                        default=0.0,
                        help='Temperature for model sampling (default: 0.0)')

    parser.add_argument('--llm_model',
                        type=str,
                        default='gpt-4.1-nano',
                        help='LLM model to use (default: gpt-4.1-nano)')



    parser.add_argument('--or_thought',
                        action='store_true',
                        help='answer nlp with modeling solution path')
    parser.add_argument('--debug_max_try',
                        type=int,
                        default=3,
                        help='Start round number for peer reflection (default: 3)')
    parser.add_argument('--mode',
                        type=str,
                        default='formalized',
                        choices=[
                            'formalized', 'wo_understanding', 'formalized_understanding_simplified', 'formalized_build_simplified'
                        ],
                        help='Ablation experiment: ORThought mode (default: formalized)')

    parser.add_argument('--patterns',
                        type=str,
                        nargs='+',
                        default=['standard'],
                        help='Baseline patterns to run (default: standard)')
    parser.add_argument('--reflexion',
                        action='store_true')
    parser.add_argument('--reflection_round',
                        type=int,
                        default=1,
                        help='Round number for reflection (default: 1)')
    parser.add_argument('--start_round',
                        type=int,
                        default=0,
                        help='Start round number for peer reflection (default: 0)')
    
    parser.add_argument('--execute_code',
                        action='store_true',
                        help='Execute generated code and compare results')
    
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    console = Console()
    dataset_names = args.dataset_name
    item_num = args.item_num
    item_range = tuple(
        args.item_range
    ) if args.item_range else None  # Use range if provided, else None
    problems = args.problems
    round_mark = args.round_mark
    temperature = args.temperature
    llm_model = args.llm_model
    patterns_to_run = args.patterns

    for dataset_name in dataset_names:
        
        results_root = f"result/{llm_model}/temp{temperature}/round{round_mark}"

        # Initialize dataset with or without item range
        if item_range:
            dataset = Dataset(dataset_name=dataset_name, item_range=item_range, problems=problems)
        else:
            dataset = Dataset(dataset_name=dataset_name, problems=problems)

        # Define all available baselines (except for 'reflexion')
        all_patterns = [
            "standard",
            "zero-shot_cot",
            "self_consistency",
        ]

        # Filter patterns to run based on input
        patterns = [p for p in all_patterns if p in patterns_to_run]
        if not patterns:
            raise ValueError(
                "No valid patterns specified. Please check your input.")
            
        """ORThought"""
        if args.or_thought and not args.execute_code:
            base_pattern = f"orthought_{args.mode}"
            console.print(f"ORThought mode: {base_pattern}", style="bold yellow")
            
            console.print(
                Panel.fit(
                    f" |Dataset: {dataset_name}  |Base pattern: {base_pattern}  |LLM Model: {llm_model}  |Round {round_mark}",
                    style="bold blue",
                    title=f"ORTHOUGHT MODEL AGENT",
                ))
            model_agent = ORThoughtModelAgent()
            save_path = os.path.join(results_root, dataset.dataset_name)
            os.makedirs(save_path, exist_ok=True)
            model_agent(dataset=dataset,
                        item_num=item_num,
                        save_path=save_path,
                        llm_model=llm_model,
                        temperature=temperature,
                        mode=args.mode)

            console.print(f"Call Solve Agent. Debugging max try: {args.debug_max_try}", style="bold yellow")
            console.print(
                Panel.fit(
                    f" |Dataset: {dataset_name}  |Base pattern: {base_pattern}  |LLM Model: {llm_model}  |Round {round_mark}",
                    style="bold blue",
                    title="ORTHOUGHT SOLVE AGENT",
                ))
            solve_agent = ORThoughtSolveAgent()
            save_path = os.path.join(results_root, dataset.dataset_name)
            os.makedirs(save_path, exist_ok=True)
            solve_agent(dataset=dataset,
                        item_num=item_num,
                        save_path=save_path,
                        llm_model=llm_model,
                        temperature=temperature,
                        debug_max_try=args.debug_max_try,
                        base_pattern=base_pattern)


        elif (not args.execute_code) and (not args.reflexion):
            time_list = []
            for pattern in patterns:
                start_time = time.time()
                try:
                    print("\n\n")
                    console.print(
                        Panel(
                            f"  |Dataset:{dataset_name}  |Running pattern:{pattern}  |LLM Model:{llm_model}  |Round {round_mark}",
                            style="bold blue",
                        ))
                    console.print(f"results_root: {results_root}", style="bold green")
                    agent = Baselines()
                    save_path = os.path.join(results_root, dataset.dataset_name)
                    os.makedirs(save_path, exist_ok=True)
                    agent(dataset=dataset,
                        item_num=item_num,
                        save_path=save_path,
                        pattern=pattern,
                        llm_model=llm_model,
                        temperature=temperature)
                except Exception as e:
                    console.print(f"Error occurred: {e}", style="bold red")
                    continue
                end_time = time.time()
                duration = end_time - start_time
                avg_time = duration / len(dataset.keys)
                time_list.append((duration, avg_time))
                console.print(f"Time taken for {pattern}: {duration:.2f} seconds", style="bold yellow")
                console.print(f"Average time taken for {pattern}: {avg_time:.2f} seconds", style="bold yellow")

            print("\n\n")
            for i in range(len(time_list)):
                duration, avg_time = time_list[i]
                print(f"Time taken for {patterns[i]}: {duration:.2f} seconds")
                print(
                    f"Average time taken for {patterns[i]}: {avg_time:.2f} seconds")
        
        
        elif args.reflexion and not args.execute_code:
            """Reflexion"""
            for pattern in patterns:
                console.print()
                console.print(
                        Panel.fit(
                            f"  |Dataset:{dataset_name}  |Base pattern:{pattern}  |LLM Model:{llm_model}  |Round {round_mark}",
                            style="bold blue",
                            title="REFLEXION",
                        ))

                reflexion = Reflexion()
                save_path = os.path.join(results_root, dataset.dataset_name)
                console.print(f"results_root: {save_path}", style="bold green")
                os.makedirs(save_path, exist_ok=True)
                reflexion(dataset=dataset,
                          item_num=item_num,
                          save_path=save_path,
                          pattern="standard",
                          llm_model=llm_model,
                          temperature=temperature,
                          round_num=args.reflection_round,
                          start_round=args.start_round
                          )

        elif args.execute_code:
            for pattern in patterns:
                console.print(" Executing code generated...")
                save_path = os.path.join(results_root, dataset.dataset_name)
                pattern_path = os.path.join(save_path, pattern)

                for i in range(args.start_round,
                            args.start_round+args.reflection_round):
                    
                    if args.or_thought:
                        pattern_path = os.path.join(save_path, f"orthought_{args.mode}")
                        if args.debug_max_try>0:
                            pattern_path = os.path.join(pattern_path, "debug")
                        execution_results = execute_matching_files(
                            pattern_path, "*.py", True)
                    
                    elif args.reflexion:
                        pattern_path = os.path.join(save_path, "reflexion")
                        round_save_path = os.path.join(pattern_path, f"round_{i+1}")
                        execution_results = execute_matching_files(
                            round_save_path, f"*.py")
                        compare_results(execution_results,
                                    dataset.ground_truth,
                                    round_save_path,
                                    f"code-gt-comparison_results_{i}.json",
                                    is_ground_truth=True,
                                    prob_type=dataset.prob_type,
                                    prob_size=dataset.prob_size)

                        print(
                            f"👌 All code files have been executed and results saved in {save_path} directory"
                        )
                        continue

                    else:
                        if i == 0:
                            execution_results = execute_matching_files(
                                pattern_path, "*.py", True)
                        else:
                            execution_results = execute_matching_files(
                                pattern_path, f"*_{i}.py")

                    compare_results(execution_results,
                                    dataset.ground_truth,
                                    pattern_path,
                                    f"code-gt-comparison_results.json",
                                    is_ground_truth=True,
                                    prob_type=dataset.prob_type,
                                    prob_size=dataset.prob_size)

                    print(
                        f"👌 All code files have been executed and results saved in {pattern_path} directory"
                    )
