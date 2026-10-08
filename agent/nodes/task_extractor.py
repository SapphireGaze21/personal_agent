"""
Task Extractor node — converts raw source data into structured Task objects.
Phase 1: LLM-based extraction with Pydantic structured output.
"""

from pydantic import BaseModel, Field
from agent.state import AgentState, Task
from agent.llm import get_llm

class ExtractedTask(BaseModel):
    title: str = Field(description="Title of the assignment, exam, lab, quiz, etc.")
    task_type: str = Field(description="One of: 'assignment', 'exam', 'lab', 'quiz', 'reading', 'unknown'")
    course: str = Field(description="The course code or name (e.g., 'DBMS', 'OS')")
    deadline: str = Field(description="Deadline date in YYYY-MM-DD format if present, else empty string", default="")
    effort_hours: float = Field(description="Estimated effort in hours as a float", default=0.0)

class EmailAnalysis(BaseModel):
    is_academic: bool = Field(description="True if the email contains academic tasks, assignments, deadlines, exams, etc. False if it's general/irrelevant like a campus fest.")
    tasks: list[ExtractedTask] = Field(description="List of tasks extracted from the email. Empty if not academic.")

class LMSAnalysis(BaseModel):
    tasks: list[ExtractedTask] = Field(description="List of tasks extracted from the LMS announcement.")

def _extract_from_emails_llm(raw_emails: list[dict]) -> tuple[list[Task], int]:
    llm = get_llm()
    structured_llm = llm.with_structured_output(EmailAnalysis)
    
    tasks = []
    filtered = 0
    
    for email in raw_emails:
        subject = email.get("subject", "")
        body = email.get("body", "")
        
        prompt = f"Analyze this email and extract academic tasks if any.\nSubject: {subject}\nBody: {body}"
        try:
            analysis = structured_llm.invoke(prompt)
            if not analysis.is_academic:
                filtered += 1
            else:
                for t in analysis.tasks:
                    task: Task = {
                        "title": t.title,
                        "source": "email",
                        "details": body,
                        "course": t.course,
                        "task_type": t.task_type,
                        "effort_hours": t.effort_hours,
                        "deadline": t.deadline,
                    }
                    tasks.append(task)
        except Exception as e:
            # Fallback on LLM failure
            print(f"Error calling LLM on email: {e}")
            filtered += 1
            
    return tasks, filtered

def _extract_from_lms_llm(raw_lms: list[dict]) -> list[Task]:
    llm = get_llm()
    structured_llm = llm.with_structured_output(LMSAnalysis)
    
    tasks = []
    for item in raw_lms:
        title = item.get("title", "")
        details = item.get("details", "")
        deadline = item.get("deadline", "")
        effort = item.get("effort", "")
        
        prompt = f"Extract the academic task from this LMS announcement.\nTitle: {title}\nDetails: {details}\nDeadline: {deadline}\nEffort: {effort}"
        try:
            analysis = structured_llm.invoke(prompt)
            for t in analysis.tasks:
                task: Task = {
                    "title": t.title,
                    "source": "lms",
                    "details": details,
                    "course": t.course,
                    "task_type": t.task_type,
                    "effort_hours": t.effort_hours,
                    "deadline": t.deadline or deadline,
                }
                tasks.append(task)
        except Exception as e:
            print(f"Error calling LLM on LMS: {e}")
            
    return tasks

def task_extractor(state: AgentState) -> dict:
    """
    Convert raw source data into unified Task objects using LLM.
    """
    email_tasks, filtered_count = _extract_from_emails_llm(state.get("raw_emails", []))
    lms_tasks = _extract_from_lms_llm(state.get("raw_lms", []))

    all_tasks = email_tasks + lms_tasks

    messages = [
        f"[TaskExtractor] LLM extracted {len(email_tasks)} tasks from emails (filtered {filtered_count} non-academic)",
        f"[TaskExtractor] LLM extracted {len(lms_tasks)} tasks from LMS",
        f"[TaskExtractor] Total: {len(all_tasks)} raw tasks before dedup",
    ]

    return {
        "extracted_tasks": all_tasks,
        "messages": messages,
    }
