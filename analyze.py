import glob
import os
import json

def execute_matching_files(folder_path,
                           file_pattern="*.py",
                           exclude_mark=False):
    """
    Traverse files matching pattern, execute their functions and collect results
    
    Args:
        folder_path (str): Path to the folder containing the Python files
        file_pattern (str): Pattern to match files (e.g., "*.py")
        
    Returns:
        dict: Dictionary with filenames as keys and function return values as values
    """
    results = {}
    import types

    # Get all matching files using glob
    pattern = os.path.join(folder_path, file_pattern)
    matching_files = glob.glob(pattern)

    if exclude_mark:
        for i in range(1, 5):
            exclude_pattern = os.path.join(folder_path, f"*_{i}.py")
            exclude_files = glob.glob(exclude_pattern)
            matching_files = [
                f for f in matching_files if f not in exclude_files
            ]

    for file_path in matching_files:
        # Get the filename without extension
        file_name = os.path.basename(file_path)
        file_name_key = file_name.split('.')[0]  # Remove the .py extension
        print("Processing:", file_name_key)
        # if not exclude_mark:
        #     file_name_key = file_name_key[:-2]
        # Create a new namespace for the file
        file_namespace = {}

        try:
            # Execute the entire file content in the namespace
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()

            # Execute the file in the namespace
            exec(file_content, file_namespace)

            # Find and execute the function
            found_function = False
            for item_name, item in file_namespace.items():
                if callable(item) and not item_name.startswith('__') and isinstance(item, types.FunctionType):
                    result = item()
                    results[file_name_key] = result
                    found_function = True
                    break

            if not found_function:
                results[file_name_key] = 'Error: No callable function found'

        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            results[file_name_key] = f'Error: {str(e)}'

    return results


def compare_results(results_a: dict, results_b: dict, save_path: str, save_file_name: str, is_ground_truth=False, prob_type=None, prob_size=None):
    """
    Compare two sets of results and display in tabular format using Rich
    
    Args:
        results_a (dict): Dictionary with filenames as keys and function return values as values
        results_b (dict): Dictionary with expected results or another set of execution results
        save_path (str): Path to save the comparison results
        save_file_name (str): Name of the file to save results
        is_ground_truth (bool): Flag indicating if results_b is ground truth (True) or another execution result (False)
        prob_type (dict): Dictionary with problem keys and their problem types as values
        prob_size (dict): Dictionary with problem keys and their problem sizes as values

    Returns:
        dict: Comparison results dictionary
    """
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    from rich.progress import track

    console = Console()

    comparison_results = {}
    match_count = 0
    # total_count = len(results_a)

    # Determine which keys to process
    if is_ground_truth:
        all_keys = results_b.keys()
    else:
        all_keys = set(results_a.keys()).union(set(results_b.keys()))

    total_count = len(all_keys)
    
    # Determine column headers based on comparison type
    result_a_label = "Result" if is_ground_truth else "Result A"
    result_b_label = "Ground Truth" if is_ground_truth else "Result B"

    # Create and style the main table
    table = Table(
        show_header=True,
        box=box.ROUNDED,
        header_style="bold magenta",
        border_style="blue"
    )

    # Add columns based on whether problem_type is provided
    table.add_column("Key", style="cyan")
    if prob_type:
        table.add_column("Type", style="yellow")
    if prob_size:
        table.add_column("Size", style="blue")
    table.add_column("Status", style="bold")
    table.add_column(result_a_label)
    table.add_column(result_b_label)

    # Print header
    console.print(
        Panel.fit("            RESULTS COMPARISON            ",
                  subtitle="Comparing with Ground Truth"
                  if is_ground_truth else "Comparing two execution results",
                  style="bold green"))

    # Track problem type statistics if provided
    problem_type_stats = {}
    if prob_type:
        for key, type_value in prob_type.items():
            if type_value not in problem_type_stats:
                problem_type_stats[type_value] = {
                    "total": 0,
                    "matched": 0
                }

    # Track problem size statistics if provided
    problem_size_stats = {}
    if prob_size:
        for key, size_value in prob_size.items():
            if size_value not in problem_size_stats:
                problem_size_stats[size_value] = {
                    "total": 0,
                    "matched": 0
                }

    match_keys = []
    # Process each result
    for key in all_keys:
        status = "NO MATCH"
        status_style = "red"  # Default status style
        result_a_str = "N/A"
        result_b_str = "N/A"
        problem_type_str = prob_type.get(key, "Unknown") if prob_type else None
        problem_size_str = prob_size.get(key, "Unknown") if prob_size else None

        has_a = key in results_a
        has_b = key in results_b

        if has_a:
            result_a_str = str(results_a[key])

        if has_b:
            result_b_str = str(results_b[key])

        if has_a and has_b:
            if isinstance(results_a[key], (int, float)) and isinstance(results_b[key], (int, float)):
                if abs(results_a[key] - results_b[key]) < 0.01:
                    is_match = True
                else:
                    is_match = False
            # if results_a[key] is a tuple or list, compare the first element
            elif isinstance(results_a[key], (tuple, list)) and isinstance(results_b[key], (int, float, str, type(None))):
                is_match = results_a[key][0] == results_b[key]
            else:
                is_match = results_a[key] == results_b[key]

            status_style = "green" if is_match else "red"
            status = "MATCH" if is_match else "MISMATCH"

            if is_match:
                match_count += 1
                match_keys.append(key)

            # Update problem type statistics
            if prob_type and key in prob_type:
                type_val = prob_type[key]
                problem_type_stats[type_val]["total"] += 1
                if is_match:
                    problem_type_stats[type_val]["matched"] += 1

            # Update problem size statistics
            if prob_size and key in prob_size:
                size_val = prob_size[key]
                problem_size_stats[size_val]["total"] += 1
                if is_match:
                    problem_size_stats[size_val]["matched"] += 1

            comparison_results[key] = {
                "matched": is_match,
                "result_a": results_a[key],
                "result_b": results_b[key]
            }
            if prob_type and key in prob_type:
                comparison_results[key]["problem_type"] = prob_type[key]
            if prob_size and key in prob_size:
                comparison_results[key]["problem_size"] = prob_size[key]

        elif has_a and not has_b:
            status = "ONLY IN A"
            status_style = "yellow"
            comparison_results[key] = {
                "matched": False,
                "result_a": results_a[key],
                "result_b": None
            }
            if prob_type and key in prob_type:
                comparison_results[key]["problem_type"] = prob_type[key]
                problem_type_stats[prob_type[key]]["total"] += 1
            if prob_size and key in prob_size:
                comparison_results[key]["problem_size"] = prob_size[key]
                problem_size_stats[prob_size[key]]["total"] += 1

        elif not has_a and has_b:
            status = "ONLY IN B"
            status_style = "yellow"
            comparison_results[key] = {
                "matched": False,
                "result_a": None,
                "result_b": results_b[key]
            }
            if prob_type and key in prob_type:
                comparison_results[key]["problem_type"] = prob_type[key]
            if prob_size and key in prob_size:
                comparison_results[key]["problem_size"] = prob_size[key]

        # Add the row to the table
        row_data = [key]
        if prob_type:
            row_data.append(problem_type_str)
        if prob_size:
            row_data.append(problem_size_str)
        row_data.extend([
            f"[{status_style}]{status}[/{status_style}]",
            result_a_str[:20] + "..." if len(result_a_str) > 23 else result_a_str,
            result_b_str[:20] + "..." if len(result_b_str) > 23 else result_b_str
        ])
        table.add_row(*row_data)

    # Display the main results table
    console.print(table)

    # Add summary information
    if total_count > 0:
        accuracy = match_count / total_count * 100
    else:
        accuracy = 0

    comparison_results["__summary__"] = {
        "total_count": total_count,
        "match_count": match_count,
        "accuracy": accuracy
    }

    # Add problem type statistics to summary
    if prob_type:
        comparison_results["__summary__"]["problem_type_stats"] = {}

        # Create a table for problem type analysis
        type_table = Table(
            show_header=True,
            box=box.SIMPLE_HEAD,
            header_style="bold yellow",
            title="Problem Type Analysis"
        )

        type_table.add_column("Problem Type", style="cyan")
        type_table.add_column("Accuracy", justify="right")
        type_table.add_column("Matched", justify="right")
        type_table.add_column("Total", justify="right")

        for type_name, stats in problem_type_stats.items():
            if stats["total"] > 0:
                type_accuracy = (stats["matched"] / stats["total"]) * 100
            else:
                type_accuracy = 0

            # Add the type statistics row
            type_table.add_row(
                type_name,
                f"{type_accuracy:.2f}%",
                str(stats["matched"]),
                str(stats["total"])
            )

            comparison_results["__summary__"]["problem_type_stats"][type_name] = {
                "total": stats["total"],
                "matched": stats["matched"],
                "accuracy": type_accuracy
            }

        # Display the problem type analysis table
        console.print("\n")
        console.print(type_table)

    # Add problem size statistics to summary
    if prob_size:
        comparison_results["__summary__"]["problem_size_stats"] = {}

        # Create a table for problem size analysis
        size_table = Table(
            show_header=True,
            box=box.SIMPLE_HEAD,
            header_style="bold blue",
            title="Problem Size Analysis"
        )

        size_table.add_column("Problem Size", style="cyan")
        size_table.add_column("Accuracy", justify="right")
        size_table.add_column("Matched", justify="right")
        size_table.add_column("Total", justify="right")

        for size_name, stats in problem_size_stats.items():
            if stats["total"] > 0:
                size_accuracy = (stats["matched"] / stats["total"]) * 100
            else:
                size_accuracy = 0

            # Add the size statistics row
            size_table.add_row(
                size_name,
                f"{size_accuracy:.2f}%",
                str(stats["matched"]),
                str(stats["total"])
            )

            comparison_results["__summary__"]["problem_size_stats"][size_name] = {
                "total": stats["total"],
                "matched": stats["matched"],
                "accuracy": size_accuracy
            }

        # Display the problem size analysis table
        console.print("\n")
        console.print(size_table)

    # Handle saving results to file
    if save_path:
        def process_results(data):
            if isinstance(data, dict):
                result = {}
                for k, v in data.items():
                    # Process result fields
                    if k == 'result_a' and isinstance(v, tuple) and len(v) > 0:
                        # If it's a tuple, only take the first element (target value)
                        result[k] = v[0] if isinstance(v[0], (int, float)) else str(v[0])
                    else:
                        result[k] = process_results(v)
                return result
            elif isinstance(data, list):
                return [process_results(item) for item in data]
            elif isinstance(data, tuple):
                # For tuples, only return the first element
                if len(data) > 0:
                    return data[0] if isinstance(data[0], (int, float)) else str(data[0])
                else:
                    return None
            elif hasattr(data, '__class__') and data.__class__.__name__ == 'GRB':
                return str(data)
            else:
                return data

        processed_comparison_results = process_results(comparison_results)

        # Save comparison results to a JSON file
        comparison_file = os.path.join(save_path, save_file_name)
        with open(comparison_file, "w", encoding="utf-8") as f:
            json.dump(processed_comparison_results,
                      f,
                      indent=2,
                      ensure_ascii=False)
        console.print(f"\n[green]Detailed results saved to:[/green] {comparison_file}")

    # Print summary
    accuracy_color = "green" if accuracy > 80 else "yellow" if accuracy > 50 else "red"
    if is_ground_truth:
        summary_text = f"Summary: {match_count}/{total_count} tests passed ([{accuracy_color}]{accuracy:.2f}%[/{accuracy_color}])"
    else:
        summary_text = f"Summary: {match_count}/{total_count} results match ([{accuracy_color}]{accuracy:.2f}%[/{accuracy_color}])"

    console.print("\n")
    console.print(Panel.fit(
        summary_text,
        border_style="bright_blue",
        padding=(1, 2)
    ))

    return comparison_results, match_keys
