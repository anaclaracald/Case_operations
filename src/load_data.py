"""
load_data.py — Leitura e inspeção inicial da planilha bruta.
"""

import pandas as pd
from src.config import RAW_DATA_PATH


def load_raw(path: str = RAW_DATA_PATH) -> pd.DataFrame:
    df = pd.read_excel(path, engine="openpyxl", dtype=str)
    return df


def print_summary(df: pd.DataFrame) -> None:
    """Imprime um resumo do DataFrame para diagnóstico rápido."""
    print(f"Shape: {df.shape}")
    print(f"Colunas: {list(df.columns)}")
    print(f"\nNulos por coluna:\n{df.isnull().sum().to_string()}")
    print(f"\nAmostra (5 linhas):\n{df.head(5).to_string()}")
