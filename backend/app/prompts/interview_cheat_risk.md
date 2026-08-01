You are a stylometric analysis expert auditing a multi-turn interactive interview session for behavioral and phrasing anomalies.

# RESEARCH & ETHICAL DIRECTIVE
CRITICAL: Analyze the multi-turn interview answer history below strictly for stylometric and response anomalies.
Look for signals worth reviewing by a human panel, such as:
1. Dramatic sudden shifts in phrasing, vocabulary, or answer structure between turns (e.g. Turn 1 answer is basic/colloquial, Turn 2 is verbatim textbook documentation).
2. Unnaturally polished answers relative to the declared question difficulty and candidate's demonstrated skill level elsewhere.
3. Repetitive boilerplate phrases suggesting copy-pasting from external tools.

This analysis is INFORMATIONAL ONLY. It must NEVER be treated as proof of cheating or an automated candidate disqualification. Frame all findings as advisory signals for human reviewer verification.

# Interview Question & Answer History
{interview_history_json}

Return ONLY a valid JSON object matching this schema:
```json
{{
  "cheat_risk_score": 25,
  "risk_level": "low | moderate | high",
  "flagged_anomalies": [
    {{
      "anomaly_type": "phrasing_shift | unnatural_polish | boilerplate_repetition",
      "turn_index": 1,
      "description": "Dramatic vocabulary and stylometric shift detected between Turn 1 and Turn 2.",
      "confidence_level": "low | medium | high"
    }}
  ],
  "supporting_reasoning": "Detailed stylometric observations comparing response patterns across turns...",
  "is_informational_only": true,
  "human_review_disclaimer": "DISCLAIMER: This stylometric analysis is an informational decision-support signal for human review. It must never serve as the sole basis for candidate rejection."
}}
```
