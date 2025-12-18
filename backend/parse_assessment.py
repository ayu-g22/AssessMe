import json
import re

INPUT_FILE = "assessments.json"
OUTPUT_FILE = "assessments_structured.json"

def extract(pattern, text):
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""

def parse_assessment(a, idx):
    text = a["content"]

    description = extract(
        r"#### Description\s+(.*?)\n\n####",
        text
    )

    job_levels = extract(
        r"#### Job levels\s+(.*?)\n\n####",
        text
    )

    duration = extract(
        r"Approximate Completion Time in minutes\s*=\s*(\d+)",
        text
    )

    test_type = extract(
        r"Test Type:\s*\n\s*([A-Z]+)",
        text
    )

    job_levels_list = [j.strip() for j in job_levels.split(",") if j.strip()]

    text_for_embedding = f"""
    Assessment Name: {a['name']}
    Description: {description}
    Job Levels: {', '.join(job_levels_list)}
    Test Type: {test_type}
    Duration: {duration} minutes
    """.strip()

    return {
        "id": idx,
        "name": a["name"],
        "url": a["url"],
        "description": description,
        "job_levels": job_levels_list,
        "test_type": test_type,
        "duration_minutes": int(duration) if duration.isdigit() else None,
        "text_for_embedding": text_for_embedding
    }

def main():
    data = json.load(open(INPUT_FILE, encoding="utf-8"))

    structured = [
        parse_assessment(a, i)
        for i, a in enumerate(data)
    ]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(structured, f, indent=2, ensure_ascii=False)

    print(f"✅ Structured {len(structured)} assessments with embeddings text")

if __name__ == "__main__":
    main()
