import pandas as pd
import argparse

def preprocess(input_file, output_file):
    df = pd.read_csv(input_file)
    # Simple feature engineering: encode protocol
    df['protocol'] = df['protocol'].map({'TCP': 0, 'UDP': 1, 'ICMP': 2}).fillna(-1)
    df['src_ip'] = df['src_ip'].apply(lambda x: int(''.join([f"{int(octet):03d}" for octet in x.split('.')])) if isinstance(x, str) else 0)
    df['dst_ip'] = df['dst_ip'].apply(lambda x: int(''.join([f"{int(octet):03d}" for octet in x.split('.')])) if isinstance(x, str) else 0)
    df = df.fillna(0)
    df.to_csv(output_file, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', help='Input traffic CSV file')
    parser.add_argument('--output', help='Output features CSV file')
    args = parser.parse_args()
    preprocess(args.input, args.output)
