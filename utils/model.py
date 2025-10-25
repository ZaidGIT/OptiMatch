import pandas as pd
import os
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------- Skill List ----------------
SKILLS = [
    "python", "java", "sql", "aws", "docker", "kubernetes",
    "react", "node", "javascript", "html", "css",
    "tensorflow", "pytorch", "excel", "tableau",
    "project management", "jira", "pandas"
]

# ---------------- Load CSV ----------------
def load_csv(csv_path='resume_jd.csv'):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"{csv_path} not found.")
    df = pd.read_csv(csv_path)
    df['Cleaned Resume Text'] = df['Cleaned Resume Text'].fillna('')
    df['JD Text'] = df['JD Text'].fillna('')
    return df

# ---------------- Feature Extraction ----------------
def get_embeddings(df, embed_model):
    resume_emb = embed_model.encode(df['Cleaned Resume Text'].tolist(), show_progress_bar=True)
    jd_emb = embed_model.encode(df['JD Text'].tolist(), show_progress_bar=True)
    X = np.hstack([resume_emb, jd_emb])
    return X

# ---------------- Training ----------------
def train_resume_model(csv_path='resume_jd.csv', save_models=True):
    df = load_csv(csv_path)
    
    embed_model = SentenceTransformer('all-MiniLM-L6-v2')
    X = get_embeddings(df, embed_model)
    y = df['Match'].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = MLPClassifier(hidden_layer_sizes=(128,64), max_iter=200, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Model Test Accuracy: {acc*100:.2f}%")

    if save_models:
        joblib.dump(model, 'resume_match_model.pkl')
        joblib.dump(embed_model, 'embedding_model.pkl')
        print("Saved model and embedding model.")

    return model, embed_model

# ---------------- Skills ----------------
def extract_skills(text):
    text_lower = text.lower()
    return [skill for skill in SKILLS if skill in text_lower]

def missing_skills(resume_text, jd_text):
    jd_skills = extract_skills(jd_text)
    resume_skills = extract_skills(resume_text)
    return list(set(jd_skills) - set(resume_skills))

# ---------------- Prediction ----------------
def predict_resume_match(resume_text, jd_text, model, embed_model):
    resume_emb = embed_model.encode([resume_text])
    jd_emb = embed_model.encode([jd_text])
    X_input = np.hstack([resume_emb, jd_emb])

    # Check if MLP model can be used
    use_mlp = hasattr(model, "n_features_in_") and X_input.shape[1] == model.n_features_in_

    if use_mlp:
        match_prob = model.predict_proba(X_input)[0][1]
        match_binary = int(match_prob >= 0.5)
    else:
        # fallback to cosine similarity
        sim_score = cosine_similarity(resume_emb, jd_emb)[0][0]
        match_prob = sim_score
        match_binary = int(sim_score >= 0.5)

    missing = missing_skills(resume_text, jd_text)
    return match_binary, match_prob, missing

# ---------------- Run Training ----------------
if __name__ == "__main__":
    train_resume_model()
