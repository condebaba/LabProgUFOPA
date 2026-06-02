"""Aplicação Streamlit para detecção de objetos em vídeos MP4 com YOLO26."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import BinaryIO

import streamlit as st

from yolo26_video_app.processing import process_video


DEFAULT_MODEL = "yolo26n.pt"


st.set_page_config(
    page_title="Detecção de Objetos com YOLO26",
    page_icon="🎥",
    layout="wide",
)


@st.cache_resource(show_spinner=False)
def load_model(model_name: str):
    """Carrega e mantém o modelo YOLO26 em cache entre execuções do Streamlit."""
    from ultralytics import YOLO

    return YOLO(model_name)


def save_upload(uploaded_file: BinaryIO, destination: Path) -> None:
    """Persiste o arquivo MP4 enviado pelo usuário em disco."""
    destination.write_bytes(uploaded_file.getbuffer())


def render_counts(counts: Counter[str]) -> None:
    """Exibe um resumo simples dos objetos detectados no vídeo processado."""
    if not counts:
        st.info("Nenhum objeto foi detectado com os parâmetros atuais.")
        return

    st.subheader("Resumo das detecções")
    rows = [
        {"Classe": label, "Ocorrências em frames": total}
        for label, total in counts.most_common()
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)


def main() -> None:
    st.title("Detecção de Objetos em Vídeo com YOLO26")
    st.write(
        "Envie um arquivo `.mp4`, ajuste os parâmetros e gere um novo vídeo "
        "com as caixas e rótulos dos objetos detectados pelo modelo YOLO26."
    )

    with st.sidebar:
        st.header("Configurações")
        model_name = st.text_input(
            "Modelo YOLO26",
            value=DEFAULT_MODEL,
            help=(
                "Use um peso oficial como yolo26n.pt, yolo26s.pt, "
                "yolo26m.pt, yolo26l.pt ou yolo26x.pt."
            ),
        )
        confidence = st.slider("Confiança mínima", 0.05, 0.95, 0.25, 0.05)
        image_size = st.select_slider(
            "Tamanho de inferência",
            options=[320, 416, 512, 640, 768, 1024],
            value=640,
        )
        device = st.text_input(
            "Dispositivo",
            value="",
            help="Deixe em branco para automático; use 'cpu', '0' ou '0,1' quando necessário.",
        )
        st.caption(
            "Observação: o primeiro uso pode baixar os pesos do modelo automaticamente."
        )

    uploaded_video = st.file_uploader("Selecione um vídeo MP4", type=["mp4"])
    if uploaded_video is None:
        st.warning("Envie um arquivo MP4 para iniciar a detecção.")
        return

    st.subheader("Vídeo original")
    st.video(uploaded_video)

    if not st.button("Detectar objetos", type="primary"):
        return

    progress_bar = st.progress(0, text="Preparando o processamento...")
    status = st.empty()

    def update_progress(current_frame: int, total_frames: int) -> None:
        percent = current_frame / total_frames if total_frames else 0
        progress_bar.progress(
            min(percent, 1.0),
            text=f"Processando frame {current_frame} de {total_frames}",
        )

    try:
        with TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            input_path = temporary_path / "entrada.mp4"
            output_path = temporary_path / "saida_detectada.mp4"

            save_upload(uploaded_video, input_path)
            status.info("Carregando o modelo YOLO26...")
            model = load_model(model_name.strip() or DEFAULT_MODEL)

            status.info("Executando inferência no vídeo...")
            counts = process_video(
                model=model,
                input_path=input_path,
                output_path=output_path,
                confidence=confidence,
                image_size=image_size,
                device=device.strip() or None,
                progress_callback=update_progress,
            )
            progress_bar.progress(1.0, text="Processamento concluído")
            status.success("Detecção concluída com sucesso!")

            output_bytes = output_path.read_bytes()
            st.subheader("Vídeo com detecções")
            st.video(output_bytes)
            st.download_button(
                "Baixar vídeo processado",
                data=output_bytes,
                file_name="video_detectado_yolo26.mp4",
                mime="video/mp4",
            )
            render_counts(counts)
    except Exception as exc:  # noqa: BLE001 - mensagem amigável para a interface web
        progress_bar.empty()
        status.error(f"Não foi possível processar o vídeo: {exc}")
        st.stop()


if __name__ == "__main__":
    main()
