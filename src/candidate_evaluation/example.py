"""
Verification script for Candidate Evaluation.
"""

import json
from candidate_evaluation.evaluator_agent import evaluate_candidate

# Sample Offer: Senior Python Developer
offer = {
    "job_title": "Senior Python Developer",
    "company_name": "TechCorp AI",
    "description": "We are looking for a Senior Python Developer to join our AI team. You will build scalable backend services.",
    "mandatory_skills": ["Python", "Django", "PostgreSQL", "Docker"],
    "mandatory_languages": ["English (Professional Working)"],
    "experience_required": 5,
    "location": "Remote",
    "type": "remote"
}

# Sample Candidate: Good fit
candidate_good = {
    "full_name": "Alice Smith",
    "heading": "Senior Backend Engineer | Python | Cloud",
    "experience_years": 6,
    "skills": ["Python", "Django", "FastAPI", "PostgreSQL", "Docker", "Kubernetes", "AWS"],
    "languages": ["English (Native)", "Spanish (Intermediate)"],
    "experiences": [
        {
            "role": "Senior Backend Engineer",
            "company": "CloudSol",
            "start_date": "2020-01",
            "end_date": "Present",
            "description": "Architected and built microservices using Python and Django. Managed PostgreSQL databases."
        },
        {
            "role": "Software Developer",
            "company": "StartUp Inc",
            "start_date": "2017-06",
            "end_date": "2019-12",
            "description": "Developed web applications using Python and Flask."
        }
    ]
}

# Sample Candidate: Bad fit (Junior)
candidate_bad = {
    "full_name": "Bob Junior",
    "heading": "Junior Developer",
    "experience_years": 1,
    "skills": ["Python", "HTML", "CSS"],
    "languages": ["English (Native)"],
    "experiences": [
        {
            "role": "Junior Developer",
            "company": "WebAgency",
            "start_date": "2023-01",
            "end_date": "Present",
            "description": "Building simple websites."
        }
    ]
}

def run_test():
    print("=== Testing Good Candidate ===")
    result_good = evaluate_candidate(candidate_good, offer)
    print(json.dumps(result_good, indent=2))
    
    print("\n=== Testing Bad Candidate ===")
    result_bad = evaluate_candidate(candidate_bad, offer)
    print(json.dumps(result_bad, indent=2))

if __name__ == "__main__":
    run_test()
