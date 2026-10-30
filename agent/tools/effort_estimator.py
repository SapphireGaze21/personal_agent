"""
Effort Estimator tool — predicts how many hours a task will take.

Milestone: M2 stub, M4 implementation, M7 RAG mode

Three modes, switched by EFFORT_MODE in config:

    zero_shot:  LLM guesses hours from the task text alone (baseline)
    rag_llm:    Retrieve 3 most similar past tasks from Chroma,
                give them to the LLM as context (main method)
    knn:        k-NN regression on features: task type, course,
                deliverables, grade weight (non-LLM baseline)

Output per task:
    - effort_hours: float (rejected if outside 0.5–40)
    - effort_reason: "Similar to DBMS Assignment 2, which took 7h"
    - effort_confidence: 0.0–1.0

History data lives in rag/history.csv.
Metric: mean absolute error against actual_hours on held-out rows.
"""
