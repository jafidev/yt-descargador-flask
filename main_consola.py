import os  # Importa el módulo 'os' para interactuar con el sistema operativo (ej. eliminar archivos)
import yt_dlp
from funciones_descarga import video_individual, audio_individual, playlist_audio

def main():
    # codigo principal de inicio
    print("Bienvenido al descargador de YT | By: jafi dev")

    while True:
        url = input("Ingrese URL de Youtube, (o 'salir') para terminar ")
        if url.lower() == 'salir':
            print(":( vuelve pronto")
            break

        if 'list=' in url:
            es_playlist = True 
            print("URL de playlist detectada")
            formato_playlist = input("¿Descargar playlist como (audio)?: ").lower()
            if formato_playlist == 'audio':
                print("Iniciando descarga de playlist de audio...")
                playlist_audio(url, '.') # Llama a la función de playlist



        else:
            es_playlist = False
            print("Url de video invidual detectado")
            formato = input("Descargar como (video/audio)? ").lower()
            if formato == 'video':
                print("Descargando video...")
                video_individual(url, '.') # <-- Se llama esta funcion
            elif formato == 'audio':
                print("Descargando audio...")
                audio_individual(url, '.')  #<-- Se llama esta funcion
            else:
                print("Formato no valido")

         # Aquí irá la lógica para determinar si es video o playlist,
         # preguntar el formato (audio/video) y llamar a la función de descarga
        print(f"Es playlist? {es_playlist}")

        print("Descarga exitosa!!")

        respuesta = input("Desea descargar algo mas? (s/n): ") .lower()
        if respuesta != 's':
            break
 
        print("Gracias por usar el descargador")
    
main()

