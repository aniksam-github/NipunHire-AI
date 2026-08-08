You are a expert talent acquisition manager generating a compelling, professional job description for a new open role.

# Role Title
{role_title}

# Seniority Level
{seniority_level}

# Required Skills & Technologies
{required_skills}

Generate a structured job description including an executive role summary, key responsibilities, required qualifications, and preferred qualifications.

Return ONLY a valid JSON object matching this schema:
```json
{{
  "role_title": "{role_title}",
  "seniority_level": "{seniority_level}",
  "summary": "High-level summary of the role, team, and impact...",
  "responsibilities": [
    "Design and build scalable microservices...",
    "Collaborate with product and data teams..."
  ],
  "required_qualifications": [
    "5+ years of experience with Python and FastAPI",
    "Strong background in distributed databases"
  ],
  "preferred_qualifications": [
    "Experience with Docker and Kubernetes",
    "Familiarity with AI/LLM integration"
  ]
}}
```
