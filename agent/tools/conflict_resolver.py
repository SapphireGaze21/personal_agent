"""
Conflict Resolver tool — resolves disagreements between sources.

Milestone: M2 stub, M4 implementation

Called by the orchestrator after duplicate merging.
Runs on tasks with more than one distinct deadline_claims value.

Resolution strategy:
    1. Python first: later source_time wins; professor email beats automated LMS
    2. Ambiguous cases go to the LLM
    3. Guard rule: the chosen value MUST equal one of the claims (no invention)
    4. Every resolution is stored as a ConflictRecord and shown to the user

Example:
    LMS says Oct 5, email says Oct 7 → Oct 7 chosen (email is newer)
    Conflict shown with reason so it is never silent.
"""
