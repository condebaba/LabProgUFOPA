# LabProgUFOPA

Aplicação web em Python para detecção de objetos em vídeos MP4 usando modelos Ultralytics YOLO26.

## Requisitos

- Python 3.10 ou superior
- Acesso à internet no primeiro uso para baixar os pesos oficiais do modelo, por exemplo `yolo26n.pt`

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Execução

```bash
streamlit run app.py
```

Depois de abrir a interface no navegador:

1. Envie um arquivo `.mp4` pelo campo **Selecione um vídeo MP4**.
2. Escolha o peso YOLO26 desejado, como `yolo26n.pt`, `yolo26s.pt`, `yolo26m.pt`, `yolo26l.pt` ou `yolo26x.pt`.
3. Ajuste a confiança mínima, o tamanho de inferência e o dispositivo de execução.
4. Clique em **Detectar objetos**.
5. Visualize e baixe o vídeo anotado com as caixas e rótulos dos objetos detectados.

## Estrutura

- `app.py`: interface Streamlit, upload do arquivo MP4 e exibição do resultado.
- `yolo26_video_app/processing.py`: leitura do vídeo, inferência frame a frame e gravação do MP4 anotado.
- `requirements.txt`: dependências necessárias para executar a aplicação.
