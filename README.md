# Conversor de Vídeo/Áudio

Conversor simples e eficiente para converter arquivos AVI, MKV e MP4 para MP4 (vídeo) ou MP3 (áudio).

## Recursos

- ✅ Converte AVI, MKV e MP4 para MP4 (mantendo vídeo e áudio)
- ✅ Converte AVI, MKV e MP4 para MP3 (extrai apenas áudio)
- ✅ Processamento em lote
- ✅ Versão com processamento paralelo para maior performance
- ✅ Interface simples via linha de comando
- ✅ Suporte para arrastar e soltar arquivos

## Requisitos

- Python 3.6+
- FFmpeg instalado no sistema

### Instalando FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Windows:**
Baixe de [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

## Uso

### Versão Simples
```bash
python converter.py
```

### Versão com Performance (Processamento Paralelo)
```bash
python convertermoreperformace.py
```

### Arrastar e Soltar
Você pode arrastar arquivos diretamente para o executável ou passar como argumentos:
```bash
python converter.py video1.avi video2.mkv video3.mp4
```

## Opções de Conversão

1. **MP4 (Vídeo)**: Mantém vídeo e áudio com codec H.264 e AAC
2. **MP3 (Áudio)**: Extrai apenas o áudio em formato MP3

## Saída

Os arquivos convertidos são salvos na pasta `convertida/` no mesmo diretório dos arquivos originais.

## Características Técnicas

### Conversão para MP4:
- Codec de vídeo: H.264 (libx264)
- Codec de áudio: AAC
- Qualidade: CRF 18 (alta qualidade)
- Preset: medium (balanço entre velocidade e compressão)

### Conversão para MP3:
- Bitrate: 192 kbps
- Sample rate: 44.1 kHz

## Licença

Este projeto é de código aberto e está disponível sob a licença MIT.