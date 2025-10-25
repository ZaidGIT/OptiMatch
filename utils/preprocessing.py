import re

abbrev_dict = {
    "javascript": "js",
    "typescript": "ts",
    "machine learning": "ml",
    "artificial intelligence": "ai",
    "data science": "ds",
    "deep learning": "dl",
    "r programming": "r",
    "powerpoint": "ppt",
    "react.js": "react",
    "react js": "react",
    "node js": "node",
    "vue.js": "vue",
    "vue js": "vue",
    "angular.js": "angular",
    "angular js": "angular",
    "django": "dj",
    "flask": "flask",
    "natural language processing": "nlp",
    "computer vision": "cv",
    "big data": "bd",
    "cloud computing": "cc",
    "amazon web services": "aws",
    "google cloud platform": "gcp",
    "microservices": "ms",
    "restful api": "api",
    "application programming interface": "api",
    "continuous integration": "ci",
    "continuous deployment": "cd",
    "devops": "devops",
    "kubernetes": "k8s",
    "docker": "docker",
    "postgresql": "psql",
    "mysql": "mysql",
    "mongodb": "mongo",
    "redis": "redis",
    "apache spark": "spark",
    "hadoop": "hadoop",
    "linux": "linux",
    "unix": "unix",
    "git": "git",
    "github": "github",
    "bitbucket": "bitbucket",
    "azure": "azure",       
    "tensorflow": "tf",
    "node.js": "node",
    "express.js": "express",
    "c++": "cpp",
    "c#": "csharp",
    "html": "html",
    "css": "css",
    "sql": "sql",
    "no sql": "nosql",
    "restful api": "api",
    "application programming interface": "api",
    "object oriented programming": "oop",
    "user interface": "ui",
    "user experience": "ux",
    "data visualization": "dv",
    "data engineering": "de",
    "business intelligence": "bi",
    "html5": "html",
    "css3": "css",
}

def abbreviate_terms(text):
    for long_form, short_form in abbrev_dict.items():
        pattern = r'\b' + re.escape(long_form) + r'\b'
        text = re.sub(pattern, short_form, text, flags=re.IGNORECASE)
    return text

def clean_text(text):
    # convert to lower case
    text = text.lower()

    # remove special char
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)

    # remove extra spaces, new lines and tabs
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'\n+', '\n', text).strip()

    # noise removal: emails, phone numbers, urls, bullet points, symbols, non-ascii characters
    text = re.sub(r'\S+@\S+', ' ', text)  # remove emails
    text = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b[;:]?', ' ', text)
    # remove phone numbers (US/International formats)
    text = re.sub(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}', ' ', text)  # remove phone numbers
    text = re.sub(r'http\S+|www\S+', ' ', text)  # remove urls
    text = re.sub(r'[\u2022\u2023\u25E6\u2043\u2219]', ' ', text)  # remove bullet points
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # remove non-ascii characters

    # section handling: skills, experience, education
    text = re.sub(r'\b(skills|experience|education|projects|certifications)\b', r'\1:', text)
    text = re.sub(r'\n+', '\n', text).strip()

    # punctuation and formatting, normalize hypens and dashes
    text = re.sub(r'[-–—]', ' - ', text)
    text = re.sub(r'([.,!?])', r' \1 ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    # abbreviation step
    text = abbreviate_terms(text)

    return text
