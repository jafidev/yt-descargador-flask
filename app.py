from flask import Flask, render_template, request, send_file, after_this_request, make_response
import os
import shutil
import uuid
import time # Se mantiene importado por si se necesita para otros usos, pero el sleep de limpieza se quita.

# Importa tus funciones de descarga desde funciones_descarga.py
from funciones_descarga import descargar_video_individual, descargar_audio_individual, descargar_playlist_audio

app = Flask(__name__)

DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'downloads_temp')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True) # Crea la carpeta si no existe

@app.route('/')
def index():
    return render_template('index.html', message=None, error=None)

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    download_type = request.form.get('download_type')
    
    if not url:
        return render_template('index.html', error="Por favor, ingresa una URL.")

    file_to_send = None # Variable para almacenar la ruta del archivo que enviaremos al usuario
    
    try:
        # Llama a la función de descarga apropiada basada en la selección del usuario.
        if 'list=' in url and download_type == 'playlist_audio':
            print(f"DEBUG: Llamando a descargar_playlist_audio para {url}")
            file_to_send = descargar_playlist_audio(url, DOWNLOAD_FOLDER) # Retorna la ruta del ZIP

        elif download_type == 'video':
            print(f"DEBUG: Llamando a descargar_video_individual para {url}")
            file_to_send = descargar_video_individual(url, DOWNLOAD_FOLDER) # Retorna la ruta del MP4

        elif download_type == 'audio':
            print(f"DEBUG: Llamando a descargar_audio_individual para {url}")
            file_to_send = descargar_audio_individual(url, DOWNLOAD_FOLDER) # Retorna la ruta del MP3

        else:
            return render_template('index.html', error="Tipo de descarga no válido o la URL no coincide con el tipo de descarga seleccionada.")

        # =========================================================================
        # Lógica para ENVIAR el archivo al navegador y LIMPIAR después
        # =========================================================================
        if file_to_send and os.path.exists(file_to_send):
            # Preparamos la respuesta que enviará el archivo al navegador.
            response = make_response(send_file(
                file_to_send, 
                as_attachment=True, 
                download_name=os.path.basename(file_to_send)
            ))
            
            # Definimos la función de limpieza que se ejecutará DESPUÉS de que Flask envíe la respuesta.
            @after_this_request
            def remove_downloaded_file_from_server(resp):
                # En entornos Linux (como Render), el archivo se libera casi inmediatamente.
                # No necesitamos time.sleep ni reintentos aquí.
                try:
                    if os.path.exists(file_to_send): 
                        os.remove(file_to_send)
                        print(f"DEBUG: Archivo temporal eliminado del servidor: {file_to_send}")
                    else:
                        print(f"DEBUG: Archivo temporal {file_to_send} ya no existe en el servidor o ya fue eliminado por yt-dlp.")
                except Exception as e:
                    # En producción, esto podría indicar un problema más serio si no es WinError 32
                    print(f"ERROR: No se pudo eliminar el archivo temporal {file_to_send} del servidor: {e}")
                return resp 
            
            return response

        else:
            return render_template('index.html', error="No se pudo obtener el archivo descargado. Verifica la URL o inténtalo de nuevo.")

    except Exception as e:
        print(f"ERROR: Fallo general en la descarga: {e}")
        return render_template('index.html', error=f"Ocurrió un error durante la descarga: {e}. Por favor, verifica la URL o inténtalo de nuevo.")

if __name__ == '__main__':
    app.run(debug=True)
