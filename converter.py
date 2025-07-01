#!/usr/bin/env python3
import subprocess
import os
import sys
from pathlib import Path

def check_ffmpeg():
    """Verifica se o FFmpeg está instalado"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def convert_file(input_file, to_mp3=False):
    """Converte um único arquivo"""
    print(f"🔄 Convertendo: {os.path.basename(input_file)}")
    
    # Criar pasta de saída
    input_dir = os.path.dirname(input_file)
    output_dir = os.path.join(input_dir, "convertida")
    os.makedirs(output_dir, exist_ok=True)
    
    # Definir arquivo de saída
    input_name = Path(input_file).stem
    output_ext = "mp3" if to_mp3 else "mp4"
    output_file = os.path.join(output_dir, f"{input_name}.{output_ext}")
    
    # Comando ffmpeg para conversão
    if to_mp3:
        # Conversão para MP3 (apenas áudio)
        cmd = [
            'ffmpeg',
            '-i', input_file,
            '-vn',              # Sem vídeo
            '-acodec', 'mp3',   # Codec MP3
            '-ab', '192k',      # Bitrate audio
            '-ar', '44100',     # Sample rate
            '-y',               # Sobrescrever se existir
            output_file
        ]
    else:
        # Conversão para MP4 (vídeo)
        cmd = [
            'ffmpeg',
            '-i', input_file,
            '-c:v', 'libx264',      # Codec H264
            '-crf', '18',           # Alta qualidade
            '-preset', 'medium',    # Velocidade balanceada
            '-c:a', 'aac',          # Audio AAC
            '-b:a', '192k',         # Bitrate audio
            '-movflags', '+faststart',  # Otimização
            '-y',                   # Sobrescrever se existir
            output_file
        ]
    
    try:
        # Executar conversão (mostra output do ffmpeg)
        result = subprocess.run(cmd, text=True)
        
        if result.returncode == 0:
            print(f"✅ Sucesso: {os.path.basename(output_file)}")
            return True
        else:
            print(f"❌ Erro ao converter: {os.path.basename(input_file)}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("    CONVERSOR AVI/MKV/MP4 → MP4/MP3")
    print("=" * 60)
    
    # Verificar FFmpeg
    if not check_ffmpeg():
        print("❌ FFmpeg não encontrado!")
        print("   Instale o FFmpeg: https://ffmpeg.org/download.html")
        input("\nPressione Enter para sair...")
        sys.exit(1)
    
    # Verificar argumentos da linha de comando
    if len(sys.argv) > 1:
        # Arquivos passados como argumentos (arrastar e soltar)
        files = sys.argv[1:]
    else:
        # Modo interativo
        print("\n📁 MODO INTERATIVO")
        print("Digite os caminhos dos arquivos ou pasta:")
        print("(ou arraste os arquivos para este programa)")
        print()
        
        files = []
        while True:
            path = input("Arquivo/Pasta (ou 'fim' para começar): ").strip().strip('"\'')
            
            if path.lower() == 'fim':
                break
            
            if os.path.isfile(path):
                files.append(path)
                print(f"✅ Adicionado: {os.path.basename(path)}")
            elif os.path.isdir(path):
                # Buscar arquivos AVI, MKV e MP4 na pasta
                for ext in ['*.avi', '*.mkv', '*.mp4']:
                    found = list(Path(path).glob(ext))
                    files.extend([str(f) for f in found])
                print(f"✅ Pasta adicionada: {len(list(Path(path).glob('*.avi')) + list(Path(path).glob('*.mkv')) + list(Path(path).glob('*.mp4')))} arquivos")
            else:
                print(f"❌ Não encontrado: {path}")
    
    # Filtrar apenas arquivos AVI, MKV e MP4
    video_files = [f for f in files if f.lower().endswith(('.avi', '.mkv', '.mp4')) and os.path.isfile(f)]
    
    if not video_files:
        print("❌ Nenhum arquivo AVI, MKV ou MP4 encontrado!")
        input("\nPressione Enter para sair...")
        sys.exit(1)
    
    print(f"\n🎬 Encontrados {len(video_files)} arquivos para converter:")
    for i, file in enumerate(video_files, 1):
        print(f"  {i}. {os.path.basename(file)}")
    
    # Escolher tipo de conversão
    print(f"\n📋 Escolha o tipo de conversão:")
    print("  1. Converter para MP4 (vídeo)")
    print("  2. Converter para MP3 (apenas áudio)")
    
    conv_type = input("\nEscolha (1/2): ").strip()
    
    if conv_type not in ['1', '2']:
        print("❌ Opção inválida")
        sys.exit(0)
    
    to_mp3 = (conv_type == '2')
    output_format = "MP3" if to_mp3 else "MP4"
    
    # Confirmar conversão
    print(f"\n🚀 Converter {len(video_files)} arquivos para {output_format}?")
    choice = input("(s/n): ").lower()
    
    if choice != 's':
        print("❌ Conversão cancelada")
        sys.exit(0)
    
    # Converter arquivos
    print(f"\n{'='*60}")
    print("🔄 INICIANDO CONVERSÕES")
    print(f"{'='*60}")
    
    success_count = 0
    for i, file in enumerate(video_files, 1):
        print(f"\n[{i}/{len(video_files)}] ", end="")
        if convert_file(file, to_mp3):
            success_count += 1
    
    # Resultado final
    print(f"\n{'='*60}")
    print("📊 CONVERSÃO FINALIZADA")
    print(f"{'='*60}")
    print(f"✅ Sucessos: {success_count}/{len(video_files)}")
    print(f"📁 Arquivos salvos na pasta 'convertida'")
    
    input("\nPressione Enter para sair...")

if __name__ == "__main__":
    main()