"""Rotinas de processamento de vídeo para inferência YOLO26."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from pathlib import Path
from typing import Any


ProgressCallback = Callable[[int, int], None]


def _open_video(capture: Any, input_path: Path) -> tuple[int, int, float, int]:
    """Valida o vídeo de entrada e retorna suas principais propriedades."""
    import cv2

    if not capture.isOpened():
        raise ValueError(f"Não foi possível abrir o vídeo: {input_path}")

    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = float(capture.get(cv2.CAP_PROP_FPS)) or 30.0
    total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

    if width <= 0 or height <= 0:
        raise ValueError("O vídeo informado não possui dimensões válidas.")

    return width, height, fps, total_frames


def _count_result_classes(
    result: Any, class_names: dict[int, str] | list[str]
) -> Counter[str]:
    """Conta as classes detectadas em um frame a partir do resultado da Ultralytics."""
    counts: Counter[str] = Counter()
    boxes = getattr(result, "boxes", None)
    if boxes is None or getattr(boxes, "cls", None) is None:
        return counts

    for class_id in boxes.cls.tolist():
        index = int(class_id)
        label = (
            class_names[index]
            if isinstance(class_names, list)
            else class_names.get(index, str(index))
        )
        counts[str(label)] += 1
    return counts


def process_video(
    *,
    model: Any,
    input_path: Path,
    output_path: Path,
    confidence: float = 0.25,
    image_size: int = 640,
    device: str | None = None,
    progress_callback: ProgressCallback | None = None,
) -> Counter[str]:
    """Processa um MP4 frame a frame e salva um novo vídeo anotado.

    Args:
        model: Instância de ``ultralytics.YOLO`` já carregada.
        input_path: Caminho do vídeo MP4 de entrada.
        output_path: Caminho para salvar o MP4 anotado.
        confidence: Limite mínimo de confiança para as detecções.
        image_size: Tamanho usado pela inferência do modelo.
        device: Dispositivo de execução aceito pela Ultralytics, como ``cpu`` ou ``0``.
        progress_callback: Função chamada com ``frame_atual`` e ``total_frames``.

    Returns:
        Um contador com a frequência das classes detectadas ao longo dos frames.
    """
    import cv2

    capture = cv2.VideoCapture(str(input_path))
    width, height, fps, total_frames = _open_video(capture, input_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    codec = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(output_path), codec, fps, (width, height))
    if not writer.isOpened():
        capture.release()
        raise ValueError(f"Não foi possível criar o vídeo de saída: {output_path}")

    aggregate_counts: Counter[str] = Counter()
    frame_number = 0

    try:
        while True:
            success, frame = capture.read()
            if not success:
                break

            frame_number += 1
            prediction_kwargs: dict[str, Any] = {
                "conf": confidence,
                "imgsz": image_size,
                "verbose": False,
            }
            if device:
                prediction_kwargs["device"] = device

            results = model.predict(frame, **prediction_kwargs)
            result = results[0]
            aggregate_counts.update(_count_result_classes(result, model.names))
            annotated_frame = result.plot()
            writer.write(annotated_frame)

            if progress_callback is not None:
                progress_callback(frame_number, total_frames or frame_number)
    finally:
        capture.release()
        writer.release()

    if frame_number == 0:
        raise ValueError("O vídeo informado não possui frames para processamento.")

    return aggregate_counts
