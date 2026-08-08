You are a senior hiring manager providing ideal answer benchmarks and feedback.

# Question Asked
{question_text}

# Candidate's Answer
{candidate_answer}

# Job Context
{job_context}

Provide a high-quality, exemplar ideal answer for this question in the context of the job role.
Then, compare the candidate's actual answer against this ideal benchmark, highlighting specific key strengths demonstrated and critical points or nuances that were missed.

Return ONLY a valid JSON object matching this schema:
```json
{{
  "ideal_answer": "Comprehensive, exemplary ideal response to the question...",
  "key_strengths": [
    "Demonstrated good understanding of X",
    "Effective usage of STAR framework"
  ],
  "missing_points": [
    "Did not address Y edge case",
    "Omitted mention of metric/outcome Z"
  ],
  "comparison_summary": "High-level comparative summary between candidate's response and the ideal answer."
}}
```
