import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import argparse

def train_model(input_file, model_file):
    df = pd.read_csv(input_file)
    X = df.drop(columns=['label'], errors='ignore')
    y = df['label'] if 'label' in df.columns else [0]*len(df)
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)
    joblib.dump(clf, model_file)
    print(f"Model saved to {model_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', help='Input features CSV file')
    parser.add_argument('--model', help='Output model file (.pkl)')
    args = parser.parse_args()
    train_model(args.input, args.model)
