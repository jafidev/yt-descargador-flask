import yt_dlp
import os
import glob
import zipfile
import uuid
import shutil
import re 
import time 

# CONFIGURACIÓN GLOBAL DE FFMPEG
# En Render, esta variable de entorno se establecerá a './ffmpeg'
# En local, si no está configurada como variable de entorno, usará la ruta de Windows.
FFMPEG_BIN_PATH = os.environ.get('FFMPEG_BIN_PATH', r'C:\ffmpeg\ffmpeg-7.1.1\bin')

# User-Agent para imitar un navegador moderno (puede ayudar a evitar detecciones de bot)
# Es una cadena común que se encuentra en navegadores Chrome.
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'


def descargar_video_individual(url, ruta_descarga='.'):
    """
    Descarga un video individual de YouTube como MP4 y devuelve la ruta del archivo descargado.
    """
    try:
        with yt_dlp.YoutubeDL({'quiet': True, 'verbose': False, 'noplaylist': True, 'user_agent': DEFAULT_USER_AGENT}) as ydl_info:
            info_dict = ydl_info.extract_info(url, download=False)
            video_title = info_dict.get('title', 'video_desconocido')
            video_title = re.sub(r'[\\/:*?"<>|]', '', video_title) 

        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(ruta_descarga, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'quiet': True, 
            'verbose': False,
            'merge_output_format': 'mp4',
            'ffmpeg_location': FFMPEG_BIN_PATH, 
            'user_agent': DEFAULT_USER_AGENT, # Añadido user-agent aquí
        }

        print(f"DEBUG: Preparando descarga de video de: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True) 
            
            final_path = info.get('filepath') 
            
            if not final_path and 'requested_downloads' in info:
                for dl_info in info['requested_downloads']:
                    if 'filepath' in dl_info:
                        final_path = dl_info['filepath']
                        break 

            if not final_path or not os.path.exists(final_path):
                list_of_files = glob.glob(os.path.join(ruta_descarga, f"{video_title}*.mp4"))
                if list_of_files:
                    final_path = max(list_of_files, key=os.path.getctime)
            
            if final_path and os.path.exists(final_path):
                print(f"DEBUG: Video descargado exitosamente en: {final_path}")
                return final_path
            else:
                raise Exception("No se pudo encontrar el archivo de video MP4 descargado.")

    except Exception as e:
        print(f"ERROR en descargar_video_individual: {e}")
        raise 

def descargar_audio_individual(url, ruta_descarga='.'):
    """
    Descarga el audio de un video individual de YouTube como MP3 y devuelve la ruta.
    """
    try:
        with yt_dlp.YoutubeDL({'quiet': True, 'verbose': False, 'noplaylist': True, 'user_agent': DEFAULT_USER_AGENT}) as ydl_info:
            info_dict = ydl_info.extract_info(url, download=False)
            audio_title = info_dict.get('title', 'audio_desconocido')
            audio_title = re.sub(r'[\\/:*?"<>|]', '', audio_title)

        ydl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': os.path.join(ruta_descarga, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'quiet': True, 
            'verbose': False,
            'ffmpeg_location': FFMPEG_BIN_PATH,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192', 
            }],
            'user_agent': DEFAULT_USER_AGENT, # Añadido user-agent aquí
        }

        print(f"DEBUG: Preparando descarga de audio de: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True) 
            
            final_path = info.get('filepath') 

            if not final_path and 'requested_downloads' in info:
                for dl_info in info['requested_downloads']:
                    if 'filepath' in dl_info and dl_info['filepath'].endswith('.mp3'):
                        final_path = dl_info['filepath']
                        break

            if not final_path or not os.path.exists(final_path):
                list_of_files = glob.glob(os.path.join(ruta_descarga, f"{audio_title}*.mp3")) 
                audio_files = [f for f in list_of_files if os.path.isfile(f) and not f.endswith('.part')]
                if audio_files:
                    final_path = max(audio_files, key=os.path.getctime)
            
            if final_path and os.path.exists(final_path):
                print(f"DEBUG: Audio descargado exitosamente en: {final_path} (MP3)")
                return final_path
            else:
                raise Exception("No se pudo encontrar el archivo de audio MP3 descargado.")

    except Exception as e:
        print(f"ERROR en descargar_audio_individual: {e}")
        raise 

def descargar_playlist_audio(url_playlist, ruta_descarga='.'):
    """
    Descarga todos los audios de una playlist como MP3, los comprime en un ZIP y devuelve la ruta del ZIP.
    """
    try:
        playlist_temp_dir = os.path.join(ruta_descarga, f"playlist_temp_{uuid.uuid4()}")
        os.makedirs(playlist_temp_dir, exist_ok=True)

        ydl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': os.path.join(playlist_temp_dir, '%(title)s.%(ext)s'), 
            'ignoreerrors': True, 
            'quiet': True, 
            'verbose': False,
            'ffmpeg_location': FFMPEG_BIN_PATH,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192', 
            }],
            'sleep_interval': 5, 
            'max_sleep_interval': 10, 
            'user_agent': DEFAULT_USER_AGENT, # Añadido user-agent aquí
        }

        print(f"DEBUG: Preparando descarga de playlist de audio: {url_playlist}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url_playlist])

            downloaded_files = glob.glob(os.path.join(playlist_temp_dir, '*.mp3')) 
            downloaded_audio_files = [f for f in downloaded_files if os.path.isfile(f) and not f.endswith('.part')]

            if not downloaded_audio_files:
                raise Exception("No se descargó ningún archivo de audio MP3 de la playlist.")

            playlist_info = ydl.extract_info(url_playlist, download=False)
            playlist_title = playlist_info.get('title', 'playlist_desconocida').replace(' ', '_').replace('/', '_') 
            
            zip_filename = f"{playlist_title}.zip"
            zip_filepath = os.path.join(ruta_descarga, zip_filename)

            with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zf:
                for audio_file in downloaded_audio_files:
                    zf.write(audio_file, os.path.basename(audio_file))
            
            print(f"DEBUG: Playlist '{playlist_title}' comprimida exitosamente en: {zip_filepath}")

            shutil.rmtree(playlist_temp_dir)
            print(f"DEBUG: Carpeta temporal de playlist '{playlist_temp_dir}' eliminada.")

            return zip_filepath 
            
    except Exception as e:
        print(f"ERROR en descargar_playlist_audio: {e}")
        raise 
