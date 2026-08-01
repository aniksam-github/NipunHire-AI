You are a recruiting director comparing multiple candidates side-by-side for a target job role.

# Job Specification
{job_details}

# Candidate Summaries & Evaluation Data
{candidates_data_json}

Provide a structured side-by-side comparison of the candidates. Highlight the relative strengths of each candidate, rate them across key dimensions (e.g. technical, communication, problem-solving, experience fit), identify which candidate leads on each dimension, and provide an overall comparative summary.

Return ONLY a valid JSON object matching this schema:
```json
{{
  "job_id": "job_123",
  "candidates_compared": [
    "cand_1",
    "cand_2"
  ],
  "per_candidate_breakdown": [
    {{
      "candidate_id": "cand_1",
      "full_name": "Jane Doe",
      "relative_strengths": [
        "Stronger system architecture experience",
        "Higher coding efficiency"
      ],
      "dimension_ratings": {{
        "technical": 9.0,
        "communication": 8.5,
        "experience_fit": 8.0
      }}
    }},
    {{
      "candidate_id": "cand_2",
      "full_name": "John Smith",
      "relative_strengths": [
        "More relevant industry background",
        "Excellent behavioral answers"
      ],
      "dimension_ratings": {{
        "technical": 8.0,
        "communication": 9.5,
        "experience_fit": 8.5
      }}
    }}
  ],
  "dimension_leaders": {{
    "technical": "cand_1",
    "communication": "cand_2",
    "experience_fit": "cand_2"
  }},
  "comparison_summary": "Comparative synthesis explaining the key trade-offs between candidates..."
}}
```
