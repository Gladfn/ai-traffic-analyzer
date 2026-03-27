from __future__ import annotations

from pathlib import Path
import pandas as pd


def ensure_dirs(data_dir: Path) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)


def load_csv_if_exists(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


def protocol_distribution(df: pd.DataFrame) -> pd.DataFrame:
    if "protocol" not in df.columns:
        return pd.DataFrame(columns=["protocol", "count"])
    out = df["protocol"].astype(str).value_counts().reset_index()
    out.columns = ["protocol", "count"]
    return out


def alert_summary(df: pd.DataFrame) -> pd.DataFrame:
    columns = [c for c in ["src_ip", "dst_ip", "protocol", "src_port", "dst_port", "length"] if c in df.columns]
    return df[columns].tail(50)


def recent_rows(df: pd.DataFrame, limit: int = 50) -> pd.DataFrame:
    return df.tail(limit)
