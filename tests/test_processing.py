"""Testes unitários para utilitários de processamento do YOLO26."""

from __future__ import annotations

from yolo26_video_app.processing import _count_result_classes


class FakeTensor:
    """Representa apenas a API ``tolist`` usada pela Ultralytics."""

    def __init__(self, values: list[float]) -> None:
        self._values = values

    def tolist(self) -> list[float]:
        return self._values


class FakeBoxes:
    def __init__(self, classes: list[float]) -> None:
        self.cls = FakeTensor(classes)


class FakeResult:
    def __init__(self, classes: list[float] | None) -> None:
        self.boxes = None if classes is None else FakeBoxes(classes)


def test_count_result_classes_with_list_names() -> None:
    result = FakeResult([0.0, 1.0, 1.0, 2.0])

    counts = _count_result_classes(result, ["pessoa", "carro", "bicicleta"])

    assert counts == {"pessoa": 1, "carro": 2, "bicicleta": 1}


def test_count_result_classes_without_boxes() -> None:
    result = FakeResult(None)

    counts = _count_result_classes(result, {0: "pessoa"})

    assert counts == {}
