from pytube import YouTube
import os
import requests
import json
import subprocess
import azure.cognitiveservices.speech as speechsdk
from multiprocessing.dummy import Pool as ThreadPool
from dotenv import load_dotenv
import logging

load_dotenv()


def from_file(vid_id):
    with open('results.json', 'r') as json_file:
        data = json.load(json_file)
        if vid_id in data:
            logging.info(f"Skipping {vid_id} because it is already processed")
            return

    region = os.environ.get("AZURE_REGION")
    sub = os.environ.get("AZURE_SUB")

    speech_config = speechsdk.SpeechConfig(subscription=sub, region=region)

    files = os.listdir(f'videos/{vid_id}/parts')

    def the_key(item):
        return int(item[0:3:1])

    files.sort(key=the_key)

    def process(wav_file):
        audio_input = speechsdk.AudioConfig(filename=f'videos/{vid_id}/parts/{wav_file}')
        lang = os.environ.get("SPEECH_RECOGNITION_LANGUAGE")
        if lang is not None:
            speech_config.speech_recognition_language = lang
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

        result = speech_recognizer.recognize_once_async().get()
        logging.info(f'For file {wav_file} found {result.text}')
        return result.text

    pool = ThreadPool(processes=25)
    results = pool.map(process, files)
    pool.close()
    pool.join()

    final_text = ''.join(results)

    with open('results.json', 'r') as json_file:
        data = json.load(json_file)

    data[vid_id] = final_text

    with open('results.json', 'w') as json_file:
        json.dump(data, json_file)


def download_videos():
    google_api_key = os.environ.get("GOOGLE_API_KEY")
    channel_id = os.environ.get("YT_CHANNEL_ID")
    r = requests.get(f'https://www.googleapis.com/youtube/v3/search?key={google_api_key}&channelId={channel_id}g&part=snippet,id&order=date&maxResults=100&pageToken=CGQQAA')
    videos = json.loads(r.text)

    items = videos['items']
    logging.info(len(items))
    for idx, vid in enumerate(items):
        logging.info(f'processing index {idx+1}')
        if 'videoId' not in vid['id']:
            logging.info('Skipping because it is not a video')
            continue

        id = vid['id']['videoId']
        if os.path.exists(f'videos/{id}') or id == 'MRIoLv2eMQA':
            logging.info(f'Skipping {id} because it already exists')
            continue

        logging.info(f'Downloading {id} which is {idx}/{len(items)}')
        url = f'https://www.youtube.com/watch?v={id}'
        video = YouTube(url).streams.filter(file_extension="mp4").first()
        video.download(output_path=f'./videos/{id}', filename=f'{id}.mp4', skip_existing=True)

        trim_mp4_command = f'ffmpeg -i videos/{id}/{id}.mp4 -ss 8 -acodec copy -vcodec copy videos/{id}/{id}-trimmed.mp4'
        subprocess.call(trim_mp4_command, shell=True)

        mp4_to_wav_command = f'ffmpeg -i videos/{id}/{id}-trimmed.mp4 -ab 160k -ac 2 -ar 44100 -vn videos/{id}/{id}.wav'
        subprocess.call(mp4_to_wav_command, shell=True)

        os.mkdir(f'videos/{id}/parts')

        split_wav = f'ffmpeg -i videos/{id}/{id}.wav -c copy -map 0 -segment_time 10 -f segment videos/{id}/parts/%03d{id}.wav'
        subprocess.call(split_wav, shell=True)


def main():
    download_videos()
    for vid_id in os.listdir("videos"):
        from_file(vid_id)


main()


