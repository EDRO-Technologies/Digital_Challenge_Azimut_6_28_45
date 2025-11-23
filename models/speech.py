import requests
import subprocess

from config import gigachat_token


def webm_bytes_to_mp3_bytes(webm_bytes: bytes) -> bytes:
  # Запускаем ffmpeg через пайп
  process = subprocess.Popen(
    [
      'ffmpeg',
      '-i', 'pipe:0',  # вход с stdin
      '-f', 'mp3',  # выходной формат mp3
      '-vn',  # без видео
      'pipe:1'  # вывод в stdout
    ],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
  )

  # Передаем webm-байты на вход ffmpeg и читаем mp3-байты с выхода
  mp3_bytes, error = process.communicate(input=webm_bytes)

  if process.returncode != 0:
    raise RuntimeError(f'FFmpeg error: {error.decode()}')

  return mp3_bytes


def get_text_from_speech(video_data):

    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    payload={
      'scope': 'SALUTE_SPEECH_PERS'
    }

    headers = {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept': 'application/json',
      'RqUID': '696bd40d-a265-43a4-aa03-d9dd5d7fdeb3',
      'Authorization': f'Basic {gigachat_token}'
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)

    access_token = response.json()['access_token']

    url = "https://smartspeech.sber.ru/rest/v1/speech:recognize"

    # Получаем байтовое представление аудио
    audio_bytes = webm_bytes_to_mp3_bytes(video_data)

    headers = {
      'Content-Type': 'audio/mpeg',
      'Accept': 'application/json',
      'Authorization': f'Bearer {access_token}'
    }

    response = requests.request("POST", url, headers=headers, data=audio_bytes, verify=False)

    return response.json()['result'][0]



if __name__ == '__main__':
    url = 'http://127.0.0.1:8007'

    file_path1 = '../exp/audio.webm'
    with open(file_path1, 'rb') as f:
        files = {'file': (file_path1, f)}
        response = requests.post(f'{url}/speech_to_text', files=files)

        print(response.json())
        
