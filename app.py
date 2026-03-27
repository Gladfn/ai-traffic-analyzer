from __future__ import annotations

import io
import os
from pathlib import Path
import pandas as pd
import streamlit as st

from src.capture import start_capture, stop_capture, capture_status
from src.preprocess import preprocess
from src.train_model import train_model
from src.detect import detect
from src.dashboard import (
    load_csv_if_exists,
    protocol_distribution,
    alert_summary,
    recent_rows,
    ensure_dirs,
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODEL_PATH = DATA_DIR / "model.pkl"
LIVE_PATH = DATA_DIR / "live_traffic.csv"
FEATURES_PATH = DATA_DIR / "features.csv"
ALERTS_PATH = DATA_DIR / "alerts.csv"
TRAINING_SOURCE = DATA_DIR / "sample_traffic.csv"

st.set_page_config(page_title="AI Traffic Analyzer", page_icon="🛡️", layout="wide")
ensure_dirs(DATA_DIR)


def save_uploaded_file(uploaded_file, destination: Path) -> None:
    destination.write_bytes(uploaded_file.getbuffer())


st.title("🛡️ AI Network Traffic Analyzer")
st.caption("Веб-интерфейс для захвата трафика, предобработки, обучения модели и детекта угроз")

with st.sidebar:
    st.header("Управление")
    st.write(f"Папка данных: `{DATA_DIR}`")

    st.subheader("1) Захват трафика")
    iface = st.text_input("Сетевой интерфейс (необязательно)", value="")
    packet_count = st.number_input("Сколько пакетов захватывать за запуск", min_value=0, value=0, step=100)
    if st.button("▶️ Запустить захват", use_container_width=True):
        message = start_capture(
            output_file=LIVE_PATH,
            iface=iface.strip() or None,
            packet_count=int(packet_count) if packet_count else 0,
        )
        st.success(message)
    if st.button("⏹️ Остановить захват", use_container_width=True):
        st.info(stop_capture())

    status = capture_status()
    st.metric("Статус sniffer", "Запущен" if status["running"] else "Остановлен")
    if status["pid"]:
        st.caption(f"PID: {status['pid']}")

    st.subheader("2) Импорт CSV")
    uploaded = st.file_uploader("Загрузить CSV трафика", type=["csv"])
    if uploaded and st.button("Сохранить как live_traffic.csv", use_container_width=True):
        save_uploaded_file(uploaded, LIVE_PATH)
        st.success("Файл сохранён в data/live_traffic.csv")

    st.subheader("3) Обучение")
    train_source = st.selectbox(
        "Источник обучающих данных",
        options=[str(TRAINING_SOURCE), str(FEATURES_PATH)],
        help="sample_traffic.csv — демо-датасет, features.csv — ваши уже подготовленные признаки",
    )
    if st.button("🧠 Обучить модель", use_container_width=True):
        train_model(train_source, MODEL_PATH)
        st.success(f"Модель сохранена: {MODEL_PATH.name}")

    st.subheader("4) Анализ")
    if st.button("⚙️ Нормализовать live_traffic.csv", use_container_width=True):
        preprocess(LIVE_PATH, FEATURES_PATH)
        st.success("Признаки сохранены в data/features.csv")
    if st.button("🚨 Запустить детект", use_container_width=True):
        detect(MODEL_PATH, FEATURES_PATH, ALERTS_PATH)
        st.success("Подозрительные записи выгружены в data/alerts.csv")

left, right = st.columns([2, 1])

with left:
    st.subheader("Последний трафик")
    live_df = load_csv_if_exists(LIVE_PATH)
    if live_df.empty:
        st.info("Пока нет live_traffic.csv. Можно загрузить CSV слева или запустить захват.")
    else:
        st.dataframe(recent_rows(live_df, 100), use_container_width=True, height=380)

with right:
    st.subheader("Сводка")
    alerts_df = load_csv_if_exists(ALERTS_PATH)
    st.metric("Пакетов в live_traffic.csv", len(live_df))
    st.metric("Подозрительных записей", len(alerts_df))
    if MODEL_PATH.exists():
        st.success("Модель найдена")
    else:
        st.warning("Модель ещё не обучена")

st.divider()
chart_left, chart_right = st.columns(2)

with chart_left:
    st.subheader("Распределение протоколов")
    if not live_df.empty:
        proto_df = protocol_distribution(live_df)
        st.bar_chart(proto_df.set_index("protocol"))
    else:
        st.info("Недостаточно данных для графика")

with chart_right:
    st.subheader("Сводка по алертам")
    if not alerts_df.empty:
        st.dataframe(alert_summary(alerts_df), use_container_width=True)
    else:
        st.info("Алертов пока нет")

st.divider()
with st.expander("Пайплайн и файлы проекта", expanded=False):
    st.markdown(
        """
        **Порядок работы:**
        1. Собрать или загрузить трафик в `data/live_traffic.csv`
        2. Нажать **Нормализовать** → получится `data/features.csv`
        3. Нажать **Обучить модель** (если модели нет)
        4. Нажать **Запустить детект** → получится `data/alerts.csv`

        **Важно:** реальный захват трафика через Scapy почти всегда требует запуск приложения с правами администратора/root.
        """
    )

for file_path in [LIVE_PATH, FEATURES_PATH, ALERTS_PATH]:
    if file_path.exists():
        with st.expander(f"Скачать {file_path.name}"):
            st.download_button(
                label=f"⬇️ Скачать {file_path.name}",
                data=file_path.read_bytes(),
                file_name=file_path.name,
                mime="text/csv",
                use_container_width=True,
            )
