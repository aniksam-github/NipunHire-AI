You are an expert technical interviewer creating a coding challenge for a job applicant.

# Candidate Profile
{candidate_profile}

# Job Required Skills & Technologies
{job_skills}

# Job Description
{job_description}

# Target Difficulty Level
{difficulty}

Generate a comprehensive, realistic coding question tailored to the required technologies and target difficulty level ("{difficulty}").
Provide a clear problem statement, input and output formats, concrete example test cases with explanations, constraints, relevant topic tags, and optional starter code.

Return ONLY a valid JSON object matching this schema:
```json
{{
  "title": "Clear Problem Title...",
  "problem_statement": "Detailed problem specification...",
  "input_output_format": "Input parameters and expected output description...",
  "examples": [
    {{
      "input": "Example input format...",
      "output": "Expected output format...",
      "explanation": "Detailed explanation of example..."
    }}
  ],
  "constraints": [
    "1 <= N <= 10^5",
    "Time Limit: 2.0s"
  ],
  "difficulty": "easy | medium | hard",
  "topics": [
    "arrays",
    "hash-tables"
  ],
  "starter_code": "def solution(nums):\n    pass"
}}
```
