def calculate_match_score(resume_text, jd_text, threshold=50):
    resume_words = set(resume_text.lower().split())
    jd_words = set(jd_text.lower().split())
    if not jd_words:
        return 0
    score = len(resume_words.intersection(jd_words)) / len(jd_words) * 100
    return 1 if score >= threshold else 0