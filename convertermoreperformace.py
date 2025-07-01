#!/usr/bin/env python3
import subprocess
import os
import sys
from pathlib import Path
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
import time

def check_ffmpeg():
    """Verifica se o FFmpeg está instalado"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def convert_file(input_file, process_id=1, to_mp3=False):
    """Converte um único arquivo"""
    filename = os.path.basename(input_file)
    print(f"🔄 [P{process_id}] Convertendo: {filename}")
    
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
        # Executar conversão silenciosamente para não misturar outputs
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ [P{process_id}] Sucesso: {os.path.basename(output_file)}")
            return True, filename
        else:
            print(f"❌ [P{process_id}] Erro: {filename}")
            return False, filename
            
    except Exception as e:
        print(f"❌ [P{process_id}] Erro: {filename} - {str(e)}")
        return False, filename

def get_optimal_workers():
    """Calcula número ideal de processos simultâneos"""
    cpu_count = multiprocessing.cpu_count()
    # Conversão de vídeo é pesada, então usar menos workers que CPUs
    if cpu_count >= 8:
        return 4  # Máximo 4 processos para sistemas potentes
    elif cpu_count >= 4:
        return 3  # 3 processos para sistemas médios
    else:
        return 2  # 2 processos para sistemas básicos

def convert_files_parallel(video_files, max_workers=None, to_mp3=False):
    """Converte múltiplos arquivos simultaneamente"""
    if max_workers is None:
        max_workers = get_optimal_workers()
    
    print(f"🚀 Processando {len(video_files)} arquivos com {max_workers} processos simultâneos")
    print(f"{'='*60}")
    
    success_files = []
    failed_files = []
    start_time = time.time()
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submeter todos os jobs
        future_to_file = {
            executor.submit(convert_file, file, i % max_workers + 1, to_mp3): file 
            for i, file in enumerate(video_files)
        }
        
        # Processar resultados conforme completam
        completed = 0
        for future in as_completed(future_to_file):
            completed += 1
            try:
                success, filename = future.result()
                if success:
                    success_files.append(filename)
                else:
                    failed_files.append(filename)
                
                # Mostrar progresso
                print(f"📊 Progresso: {completed}/{len(video_files)} concluídos")
                
            except Exception as e:
                filename = os.path.basename(future_to_file[future])
                failed_files.append(filename)
                print(f"❌ Erro no processo: {filename} - {str(e)}")
    
    elapsed_time = time.time() - start_time
    return success_files, failed_files, elapsed_time
def main():
    print("=" * 60)
    print("    CONVERSOR PARALELO AVI/MKV/MP4 → MP4/MP3")
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
    
    # Configurar número de processos
    optimal_workers = get_optimal_workers()
    print(f"\n⚙️  Configuração:")
    print(f"   • CPUs detectadas: {multiprocessing.cpu_count()}")
    print(f"   • Processos recomendados: {optimal_workers}")
    
    worker_choice = input(f"\nUsar {optimal_workers} processos simultâneos? (s/n ou digite número): ").strip()
    
    if worker_choice.lower() == 'n':
        try:
            max_workers = int(input("Quantos processos simultâneos? (1-8): "))
            max_workers = max(1, min(8, max_workers))
        except ValueError:
            max_workers = optimal_workers
    elif worker_choice.isdigit():
        max_workers = max(1, min(8, int(worker_choice)))
    else:
        max_workers = optimal_workers
    
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
    print(f"\n🚀 Converter {len(video_files)} arquivos para {output_format} com {max_workers} processos?")
    choice = input("(s/n): ").lower()
    
    if choice != 's':
        print("❌ Conversão cancelada")
        sys.exit(0)
    
    # Converter arquivos em paralelo
    print(f"\n{'='*60}")
    print("🔄 INICIANDO CONVERSÕES PARALELAS")
    print(f"{'='*60}")
    
    success_files, failed_files, elapsed_time = convert_files_parallel(video_files, max_workers, to_mp3)
    
    # Resultado final
    print(f"\n{'='*60}")
    print("📊 CONVERSÃO FINALIZADA")
    print(f"{'='*60}")
    print(f"✅ Sucessos: {len(success_files)}/{len(video_files)}")
    print(f"❌ Falhas: {len(failed_files)}")
    print(f"⏱️  Tempo total: {elapsed_time:.1f} segundos")
    print(f"📁 Arquivos salvos na pasta 'convertida'")
    
    if failed_files:
        print(f"\n❌ Arquivos que falharam:")
        for file in failed_files:
            print(f"   • {file}")
    
    # Calcular velocidade média
    if success_files:
        avg_time = elapsed_time / len(success_files)
        print(f"\n📈 Velocidade média: {avg_time:.1f}s por arquivo")
    
    input("\nPressione Enter para sair...")

if __name__ == "__main__":
    main()