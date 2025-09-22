standard_prompt = """
The problem description is as follows:
{}
Please provide a mathematical model and Gurobipy code to solve this problem. The code you return should be a callable function whose parameters have default values extracted from the problem, and whose return value is the optimal objective function value of the model (if it exists), otherwise return None. Your response should be this format:
```model
[Your Model]
```
```python
[Your Code]
```
"""


formalized_solution_path_prompt = r"""
You are an expert in optimization modeling and programming. Please carefully analyze the following optimization problem:

```text
{nlp}
```

Your task is to provide a comprehensive solution that includes your detailed solution path, a formal mathematical model, and executable Gurobipy Python code. Please structure your response as follows:

## 1. Solution Path

Enclose your entire solution path within **<solution_path>** and **</solution_path>** tags. This section should detail your approach to understanding and modeling the problem:

### A. Understanding the Problem
   - **Core Optimization Objective:** What is your understanding of the primary goal of this optimization problem (e.g., what is being maximized or minimized)?
   - **Key Decision Variables:**
     - Identify all the distinct choices or quantities that need to be decided.
     - For each decision variable, explain why it's a variable, its meaning in the context of the problem, and its type (e.g., continuous, integer, binary). 
   - **Main Constraints:** List and briefly describe the critical limitations, restrictions, or conditions imposed by the problem statement.

### B. Building the Mathematical Model – Step by Step
   - **Decision Variables Definition:** Formally define each decision variable using appropriate symbols. Clearly state its meaning and mathematical type (e.g., $x_{{ij}} \ge 0$ and continuous, or $y_k \in {{0,1}}$).
   - **Objective Function Construction:**
     - Clearly state whether the objective is to maximize or minimize.
     - Provide the mathematical expression for the objective function.
     - Explain the derivation of each term in the objective function, linking it directly to the problem description and the defined decision variables. Clarify how each part contributes to the overall goal.
   - **Constraint Construction:**
     - For each constraint identified from the problem description:
       - Translate it into a mathematical equation or inequality involving the decision variables.
       - Explain the logic behind its formulation, ensuring it accurately reflects the corresponding limitation in the problem statement. Address aspects like fund availability, investment limits, and cash flow between years.

## 2. Summary of the Mathematical Model

Compile the complete mathematical model. This section should clearly present all components of your optimization model. Enclose the entire model within **```model** and **```** tags.

## 3. Gurobipy Python Code

Translate your mathematical model into a complete and executable Gurobipy Python function(Everything should be defined inside of the function).
- The function has arguments **with default values extracted directly from the provided problem description**
- The function should return only the optimal objective function value if a feasible solution is found, or `None` if the problem is infeasible or unbounded.
- Enclose the Python code within **```python** and **```** tags.
"""


debug_prompt = r"""
You are an expert Gurobipy developer and debugger. Your task is to analyze the provided mathematical model, Gurobipy code, and error message to identify and fix the bug in the Gurobipy code. The corrected code must accurately implement the given mathematical model.

The problem description:

```text
{nlp}
```

The mathematical model:

```model
{model_text}
```

The Gurobipy code:

```python
{code_text}
```

The error message during code execution:

```text
{error_message}
```

Your Task:

1. Identify the Bug.
2. Provide Corrected Code: Offer a complete, corrected version of the Gurobipy code, and provide a brief explanation of the changes made.
3. Ensure Model Adherence: The corrected code must accurately reflect the provided mathematical model.

Output Format:
1. A brief explanation of fixes.
2. Corrected Gurobipy Code
  - Enclose the corrected code within **<code>** and **</code>** tags.
  - The code should be a callable function whose parameters have default values and whose return value is the optimal objective function value of the model (if it exists), otherwise return None.
"""


formalized_solution_path_build_simplified_prompt = r"""
You are an expert in optimization modeling and programming. Please carefully analyze the following optimization problem:

```text
{nlp}
```

Your task is to provide a comprehensive solution that includes your detailed solution path, a formal mathematical model, and executable Gurobipy Python code. Please structure your response as follows:

## 1. Solution Path

Enclose your entire solution path within **<solution_path>** and **</solution_path>** tags. This section should detail your approach to understanding and modeling the problem:

### A. Understanding the Problem
   - **Core Optimization Objective:** What is your understanding of the primary goal of this optimization problem (e.g., what is being maximized or minimized)?
   - **Key Decision Variables:**
     - Identify all the distinct choices or quantities that need to be decided.
     - For each decision variable, explain why it's a variable, its meaning in the context of the problem, and its type (e.g., continuous, integer, binary). 
   - **Main Constraints:** List and briefly describe the critical limitations, restrictions, or conditions imposed by the problem statement.

### B. Building the Mathematical Model – Step by Step
   Please define the mathematical model.

## 2. Summary of the Mathematical Model

Compile the complete mathematical model. This section should clearly present all components of your optimization model. Enclose the entire model within **```model** and **```** tags.

## 3. Gurobipy Python Code

Translate your mathematical model into a complete and executable Gurobipy Python function(Everything should be defined inside of the function).
- The function has arguments **with default values extracted directly from the provided problem description**
- The function should return only the optimal objective function value if a feasible solution is found, or `None` if the problem is infeasible or unbounded.
- Enclose the Python code within **```python** and **```** tags.
"""


formalized_solution_path_understanding_simplified_prompt = r"""
You are an expert in optimization modeling and programming. Please carefully analyze the following optimization problem:

```text
{nlp}
```

Your task is to provide a comprehensive solution that includes your detailed solution path, a formal mathematical model, and executable Gurobipy Python code. Please structure your response as follows:

## 1. Solution Path

Enclose your entire solution path within **<solution_path>** and **</solution_path>** tags. This section should detail your approach to understanding and modeling the problem:

### A. Understanding the Problem
   From an optimization perspective, what is your understanding of this optimization problem?

### B. Building the Mathematical Model – Step by Step
   - **Decision Variables Definition:** Formally define each decision variable using appropriate symbols. Clearly state its meaning and mathematical type (e.g., $x_{{ij}} \ge 0$ and continuous, or $y_k \in {{0,1}}$).
   - **Objective Function Construction:**
     - Clearly state whether the objective is to maximize or minimize.
     - Provide the mathematical expression for the objective function.
     - Explain the derivation of each term in the objective function, linking it directly to the problem description and the defined decision variables. Clarify how each part contributes to the overall goal.
   - **Constraint Construction:**
     - For each constraint identified from the problem description:
       - Translate it into a mathematical equation or inequality involving the decision variables.
       - Explain the logic behind its formulation, ensuring it accurately reflects the corresponding limitation in the problem statement. Address aspects like fund availability, investment limits, and cash flow between years.

## 2. Summary of the Mathematical Model

Compile the complete mathematical model. This section should clearly present all components of your optimization model. Enclose the entire model within **```model** and **```** tags.

## 3. Gurobipy Python Code

Translate your mathematical model into a complete and executable Gurobipy Python function(Everything should be defined inside of the function).
- The function has arguments **with default values extracted directly from the provided problem description**
- The function should return only the optimal objective function value if a feasible solution is found, or `None` if the problem is infeasible or unbounded.
- Enclose the Python code within **```python** and **```** tags.
"""


formalized_solution_path_wo_understanding_prompt = r"""
You are an expert in optimization modeling and programming. Please carefully analyze the following optimization problem:

```text
{nlp}
```

Your task is to provide a comprehensive solution that includes your detailed solution path, a formal mathematical model, and executable Gurobipy Python code. Please structure your response as follows:

## 1. Solution Path

Enclose your entire solution path within **<solution_path>** and **</solution_path>** tags. This section should detail your approach to understanding and modeling the problem:

### Building the Mathematical Model – Step by Step
   - **Decision Variables Definition:** Formally define each decision variable using appropriate symbols. Clearly state its meaning and mathematical type (e.g., $x_{{ij}} \ge 0$ and continuous, or $y_k \in {{0,1}}$).
   - **Objective Function Construction:**
     - Clearly state whether the objective is to maximize or minimize.
     - Provide the mathematical expression for the objective function.
     - Explain the derivation of each term in the objective function, linking it directly to the problem description and the defined decision variables. Clarify how each part contributes to the overall goal.
   - **Constraint Construction:**
     - For each constraint identified from the problem description:
       - Translate it into a mathematical equation or inequality involving the decision variables.
       - Explain the logic behind its formulation, ensuring it accurately reflects the corresponding limitation in the problem statement. Address aspects like fund availability, investment limits, and cash flow between years.

## 2. Summary of the Mathematical Model

Compile the complete mathematical model. This section should clearly present all components of your optimization model. Enclose the entire model within **```model** and **```** tags.

## 3. Gurobipy Python Code

Translate your mathematical model into a complete and executable Gurobipy Python function(Everything should be defined inside of the function).
- The function has arguments **with default values extracted directly from the provided problem description**
- The function should return only the optimal objective function value if a feasible solution is found, or `None` if the problem is infeasible or unbounded.
- Enclose the Python code within **```python** and **```** tags.
"""


feedback_prompt = """
Now based on the "Problem Description," evaluate whether the **decision variables, objective function, and constraints** in both the "Mathematical Model" and "Gurobipy Code" correctly reflect:
- All decisions to be made,
- Objectives to be optimized,
- Constraints to be respected.

Use the "Problem Description" as your primary reference. Also, consider the code execution result:

{error_message}

(Note: If `error_message` is None, the code ran successfully.)

**Key Evaluation Areas:**

1. **Decision Variables**
   - Are all necessary decision points included?
   - Are variable types (binary, integer, continuous), bounds, and indices correct per the problem description?

2. **Objective Function**
   - Does it fully capture the stated objectives?
   - Is the optimization direction (min/max) correct?
   - Are the variables and coefficients accurate?

3. **Constraints**
   - Are all limitations from the problem description included?
   - Do constraints use correct variables, coefficients, and inequality signs?
   - Are they applied to the right conditions or indices?

4. **Internal Consistency**
   - Are the "Mathematical Model" and "Gurobipy Code" aligned in terms of variables, objective, and constraints?

5. **Execution Result Analysis**
   - If there's an error message, what might have caused it?
   - Could it stem from incorrect variables, constraints, or parameter usage?

**Output Instructions:**

- If issues are found:
  1. Clearly identify where the model or code deviates from the problem description.
  2. Explain why it’s incorrect and its potential impact.
  3. Link it to the error message if applicable.

- If everything is correct:
  - Confirm that the model and code align with the problem description and are internally consistent.
"""


reflection_prompt = """
Please refine your initial answer(mathematical model and Gurobipy code) based on your feedback.
Your response should be this format:

```model
[Your Model]    
```

```python
[Your Code]
```

Important Note: The code you return should be a callable function whose parameters have default values extracted from the problem, and whose return value is the optimal objective function value of the model (if it exists), otherwise return None. 
"""
