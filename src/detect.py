import pandas as pd
import joblib
import argparse

def detect(model_file, input_file, output_file):
    clf = joblib.load(model_file)
    df = pd.read_csv(input_file)
    X = df.drop(columns=['label'], errors='ignore')
    preds = clf.predict(X)
    alert_df = df.copy()
    alert_df['alert'] = preds
    alert_df = alert_df[alert_df['alert'] == 1]  # 1 means suspicious
    alert_df.to_csv(output_file, index=False)
    print(f"Alerts saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', help='Trained model file (.pkl)')
    parser.add_argument('--input', help='Input features CSV file')
    parser.add_argument('--output', help='Output alerts CSV file')
    args = parser.parse_args()
    detect(args.model, args.input, args.output)
