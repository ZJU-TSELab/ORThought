# ORThought

A framework that leverages expert-level optimization modeling principles through chain-of-thought reasoning to automate the Optimization Modeling (OM) process.

The repo is the official implementation for the paper: [Automated Optimization Modeling through Expert-Guided Large Language Model Reasoning](https://arxiv.org/abs/2508.14410)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Apply for a Gurobi license and activate it. (The limited license obtained automatically when installing gurobipy can solve small problems; you need to activate a full license to solve large problems.)

### 2. Configure API Keys

Edit the [configuration file](config.json) with your API credentials.

### 3. Run the Experiments

```bash
python main.py --dataset_name <dataset_name(s)> --llm_model <llm_model_name> --or_thought --debug_max_try <debug_max_try> --temperature <temperature>
```

#### Example

You can quickly test one problem by run:

```bash
python main.py --dataset_name logior --llm_model gpt-4.1-nano --or_thought --debug_max_try 3 --problems prob_001
```

There is a default setting to run ORThought on 4 datasets using gpt-4.1-nano in [main.sh](main.sh):

```bash
python main.py --dataset_name complexor industryor nlp4lp logior --llm_model gpt-4.1-nano --or_thought --temperature 0.0 --debug_max_try 3
```

## Usage

### Command Line Arguments

#### Required Arguments

- `--dataset_name`: Specify one or more datasets to run experiments on
  - Options: `complexor`, `industryor`, `nlp4lp`, `logior`

- `--llm_model`: Specify the language model to use
  - Options: `gpt-4.1-nano`, `qwen3-32b`, `deepseek-chat`, etc.

#### Method Selection (choose one)

- `--or_thought`: Use ORThought method
- `--pattern`: Use baseline methods
  - Options: `standard`, `zero-shot_cot` (Chain-of-Thought), `self_consistency` (Self-Consistency)
- `--reflexion`: Use baseline Reflexion method

#### Optional Arguments

- `--temperature`: Temperature for LLM sampling (default: 0.0)
  - Range: 0.0 (deterministic) to 1.0 (more random)
  - Example: `--temperature 0.0`

- `--debug_max_try`: Maximum debug attempts for ORThought (default: 3)
  - Example: `--debug_max_try 5`

- `--reflection_round`: Number of reflection rounds for Reflexion method
  - Example: `--reflection_round 3`

- `--mode`: Ablation study mode for ORThought variants

- `--problems`: Select specific problems to run

## Datasets

The [datasets](datasets) include one newly created dataset (LogiOR) and three corrected and re-annotated existing datasets (ComplexOR, NLP4LP, IndustryOR). (Documentation of our corrections will be provided shortly.)

**LogiOR**: A comprehensive benchmark dataset comprising 92 logistics and supply chain optimization problems, developed over two months under the guidance of three Operations Research (OR) experts. The problems are adapted from classical OR solver test datasets, textbook examples, research papers, and real-world applications. LogiOR covers a broad spectrum of optimization types including Linear Programming (LP), Integer Linear Programming (ILP), Mixed-Integer Linear Programming (MILP), and Nonlinear Programming (NLP). Each problem is equipped with standardized annotations including mathematical formulations, executable Gurobi implementation code, optimal solutions, and problem characteristics (type, size metrics).

## Citation

```text
@misc{yang2025automatedoptimizationmodelingexpertguided,
      title={Automated Optimization Modeling through Expert-Guided Large Language Model Reasoning}, 
      author={Beinuo Yang and Qishen Zhou and Junyi Li and Chenxing Su and Simon Hu},
      year={2025},
      eprint={2508.14410},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2508.14410}, 
}
```
