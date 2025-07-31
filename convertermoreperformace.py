#!/usr/bin/env python3
import subprocess
import os
import sys
from pathlib import Path
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
import time
import re
from datetime import timedelta

def check_ffmpeg():
    """Verifica se o FFmpeg está instalado"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_video_duration(input_file):
    """Obtém a duração do vídeo em segundos usando ffprobe"""
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            input_file
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            duration_str = result.stdout.strip()
            # Verificar se não é N/A ou vazio
            if duration_str and duration_str != 'N/A':
                return float(duration_str)
    except:
        pass
    return None

def parse_time(time_str):
    """Converte string de tempo HH:MM:SS.ms para segundos"""
    try:
        parts = time_str.split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
        return hours * 3600 + minutes * 60 + seconds
    except:
        return 0

def format_time(seconds):
    """Formata segundos para string legível"""
    if seconds < 0:
        return "calculando..."
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"

def format_size(bytes):
    """Formata bytes para tamanho legível"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.1f} TB"

def convert_file(input_file, process_id=1, to_mp3=False, to_ac3=False, use_gpu=False):
    """Converte um único arquivo"""
    filename = os.path.basename(input_file)
    print(f"🔄 [P{process_id}] Convertendo: {filename}")
    
    # Criar pasta de saída
    input_dir = os.path.dirname(input_file)
    output_dir = os.path.join(input_dir, "convertida")
    os.makedirs(output_dir, exist_ok=True)
    
    # Definir arquivo de saída
    input_name = Path(input_file).stem
    if to_mp3:
        output_ext = "mp3"
    elif to_ac3:
        output_ext = "ac3"
    else:
        output_ext = "mp4"
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
    elif to_ac3:
        # Conversão para AC3 (apenas áudio)
        cmd = [
            'ffmpeg',
            '-i', input_file,
            '-vn',              # Sem vídeo
            '-acodec', 'ac3',   # Codec AC3
            '-ab', '640k',      # Bitrate audio (AC3 padrão)
            '-ar', '48000',     # Sample rate (AC3 padrão)
            '-y',               # Sobrescrever se existir
            output_file
        ]
    else:
        # Conversão para MP4 (vídeo)
        if use_gpu:
            # Usar aceleração por GPU com VideoToolbox no macOS
            cmd = [
                'ffmpeg',
                '-i', input_file,
                '-c:v', 'h264_videotoolbox',   # Codec H264 com VideoToolbox
                '-b:v', '3000k',                # Bitrate de vídeo para GPU
                '-c:a', 'aac',                  # Audio AAC
                '-b:a', '192k',                 # Bitrate audio
                '-movflags', '+faststart',      # Otimização
                '-y',                           # Sobrescrever se existir
                output_file
            ]
        else:
            # Usar CPU com libx264
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
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        total_time = time.time() - start_time
        
        if result.returncode == 0:
            # Obter tamanho real do arquivo
            actual_size = os.path.getsize(output_file)
            print(f"✅ [P{process_id}] Sucesso: {filename} | Tempo: {format_time(total_time)} | Tamanho: {format_size(actual_size)}")
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

def convert_files_parallel(video_files, max_workers=None, to_mp3=False, to_ac3=False, use_gpu=False):
    """Converte múltiplos arquivos simultaneamente"""
    if max_workers is None:
        max_workers = get_optimal_workers()
    
    print(f"🚀 Processando {len(video_files)} arquivos com {max_workers} processos simultâneos")
    print(f"{'='*60}")
    print(f"💡 Dica: A barra de progresso mostra o progresso individual de cada arquivo")
    
    success_files = []
    failed_files = []
    start_time = time.time()
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submeter todos os jobs
        future_to_file = {
            executor.submit(convert_file, file, i % max_workers + 1, to_mp3, to_ac3, use_gpu): file 
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
    print("    CONVERSOR PARALELO AVI/MKV/MP4/WAV → MP4/MP3/AC3")
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
            
            # Remover barras invertidas de escape (quando copia do terminal)
            path = path.replace('\\', '')
            
            if os.path.isfile(path):
                files.append(path)
                print(f"✅ Adicionado: {os.path.basename(path)}")
            elif os.path.isdir(path):
                # Buscar arquivos AVI, MKV, MP4, WAV e AC3 na pasta
                for ext in ['*.avi', '*.mkv', '*.mp4', '*.wav', '*.ac3']:
                    found = list(Path(path).glob(ext))
                    files.extend([str(f) for f in found])
                print(f"✅ Pasta adicionada: {len(list(Path(path).glob('*.avi')) + list(Path(path).glob('*.mkv')) + list(Path(path).glob('*.mp4')) + list(Path(path).glob('*.wav')) + list(Path(path).glob('*.ac3')))} arquivos")
            else:
                print(f"❌ Não encontrado: {path}")
    
    # Filtrar apenas arquivos AVI, MKV, MP4, WAV e AC3
    media_files = [f for f in files if f.lower().endswith(('.avi', '.mkv', '.mp4', '.wav', '.ac3')) and os.path.isfile(f)]
    
    if not media_files:
        print("❌ Nenhum arquivo AVI, MKV, MP4, WAV ou AC3 encontrado!")
        input("\nPressione Enter para sair...")
        sys.exit(1)
    
    print(f"\n🎬 Encontrados {len(media_files)} arquivos para converter:")
    for i, file in enumerate(media_files, 1):
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
    print("  3. Converter para AC3 (apenas áudio)")
    
    conv_type = input("\nEscolha (1/2/3): ").strip()
    
    if conv_type not in ['1', '2', '3']:
        print("❌ Opção inválida")
        sys.exit(0)
    
    to_mp3 = (conv_type == '2')
    to_ac3 = (conv_type == '3')
    
    if to_mp3:
        output_format = "MP3"
    elif to_ac3:
        output_format = "AC3"
    else:
        output_format = "MP4"
    
    # Perguntar sobre uso de GPU apenas se for conversão para MP4
    use_gpu = False
    if not to_mp3 and not to_ac3:
        print(f"\n🖥️  Usar aceleração por GPU (VideoToolbox)?")
        print("  • GPU: Mais rápido, mas qualidade fixa")
        print("  • CPU: Mais lento, mas melhor controle de qualidade")
        
        gpu_choice = input("\nUsar GPU? (s/n): ").strip().lower()
        use_gpu = (gpu_choice == 's')
        
        if use_gpu:
            print("✅ Usando aceleração por GPU (h264_videotoolbox)")
        else:
            print("✅ Usando CPU (libx264 com CRF 18)")
    
    # Confirmar conversão
    print(f"\n🚀 Converter {len(media_files)} arquivos para {output_format} com {max_workers} processos?")
    choice = input("(s/n): ").lower()
    
    if choice != 's':
        print("❌ Conversão cancelada")
        sys.exit(0)
    
    # Converter arquivos em paralelo
    print(f"\n{'='*60}")
    print("🔄 INICIANDO CONVERSÕES PARALELAS")
    print(f"{'='*60}")
    
    success_files, failed_files, elapsed_time = convert_files_parallel(media_files, max_workers, to_mp3, to_ac3, use_gpu)
    
    # Resultado final
    print(f"\n{'='*60}")
    print("📊 CONVERSÃO FINALIZADA")
    print(f"{'='*60}")
    print(f"✅ Sucessos: {len(success_files)}/{len(media_files)}")
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