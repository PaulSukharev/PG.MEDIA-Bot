import json
import os
import re
import time
import random
import http.client as httplib
import httplib2
import ffmpeg
import shutil
from googleapiclient.http import MediaFileUpload
from aiohttp import streamer

import pytube
from youtubesearchpython import *
from moviepy.editor import *
import datetime
 
from config_reader import load_config

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from googleapiclient.http import MediaFileUpload
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

import yt

months = ["unknown", "января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]

RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
  httplib.IncompleteRead, httplib.ImproperConnectionState,
  httplib.CannotSendRequest, httplib.CannotSendHeader,
  httplib.ResponseNotReady, httplib.BadStatusLine)

MAX_RETRIES = 10

httplib2.RETRIES = 1

VALID_PRIVACY_STATUSES = ('public', 'private', 'unlisted')

API_KEY = '*********'
 
APP_TOKEN_FILE = "helpers/client_secret.json"
USER_TOKEN_FILE = "config/user_token.json"

SCOPES = [
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/youtube.upload'
]

def get_creds_saved():
    os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
    # https://developers.google.com/docs/api/quickstart/python
    creds = None
 
    if os.path.exists(USER_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(USER_TOKEN_FILE, SCOPES)
 
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
 
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
 
        with open(USER_TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
 
    return creds


def get_service():
    creds = get_creds_saved()
    service = build('oauth2', 'v2', credentials=creds)
    return service


def get_service_creds(service = 'youtube', version = 'v3'):
    creds = get_creds_saved()
    service = build(service, version, credentials=creds)
    return service


async def get_video_info(link: str):
    return Video.getInfo(link, mode= ResultMode.json)


async def get_timestamps(link: str):
    youtube = pytube.YouTube(link)
    description = youtube.description.strip().encode()
    video_length = str(datetime.timedelta(seconds=youtube.length))

    times = []
    for st1 in description.split(b'\n'):
        timecode = st1.decode()
        if re.search(r'^(?:(?:([01]?\d|2[0-3]):)?([0-5]?\d):)?([0-5]?\d)', timecode):
            t1 = timecode.split(' ', 1)[0].strip()
            t2 = timecode.split(' ', 1)[1].strip()
            times.append((t1, t2))

    timecodes = []
    for i in range(len(times)):
        if i != len(times)-1:
            timecodes.append(((times[i])[0], (times[i+1])[0], (times[i])[1]))
        else:
            timecodes.append(((times[i])[0], video_length, (times[i])[1]))
    
    return timecodes

async def check_video_1080p(url: str):
    youtube = pytube.YouTube(url)
    streams = youtube.streams

    if streams == None:
        return None
    
    video = streams.filter(res='1080p', file_extension='mp4').first()
    return video

async def download_video(url: str):
    youtube = pytube.YouTube(url)
    print(youtube)

    temp_dir = 'cut_video_temp' + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    print(temp_dir)

    print(youtube.streams.filter(res='1080p', file_extension='mp4'))
    video = youtube.streams.filter(res='1080p', file_extension='mp4').first().download(output_path=f'temp/{temp_dir}', filename_prefix='video')
    audio = youtube.streams.filter(type='audio', file_extension='mp4').first().download(output_path=f'temp/{temp_dir}', filename_prefix='audio')

    video_stream = ffmpeg.input(video)
    audio_stream = ffmpeg.input(audio)

    video = 'video.mp4'
    ffmpeg.output(audio_stream, video_stream, f'temp/{temp_dir}/{video}', vcodec='copy', acodec='copy').run()

    return (video, temp_dir)


async def parse_timestamp_to_seconds(time: str):
    if len(time.split(':')) == 2:
        t = datetime.datetime.strptime(time, '%M:%S')
        return t.minute * 60 + t.second
    if len(time.split(':')) == 3:
        t = datetime.datetime.strptime(time, '%H:%M:%S')
        return t.hour * 3600 + t.minute * 60 + t.second

async def cut_video(link: str, clips: list):
    video = await download_video(link)

    cut_clips = []
    for clip in clips:
        start_time = await parse_timestamp_to_seconds(clip[0])
        end_time = await parse_timestamp_to_seconds(clip[1])
        cut_clip_path = f'temp/{video[1]}/{start_time}.mp4'
        ffmpeg_extract_subclip(f'temp/{video[1]}/{video[0]}', start_time, end_time, targetname=cut_clip_path)
        cut_clips.append((start_time, cut_clip_path, clip[2]))

    return cut_clips


async def cut_video_and_upload(link: str, clips: list):
    cut_clips = await cut_video(link, clips)
    await upload_videos_to_youtube(link, cut_clips)
    return cut_clips

async def upload_videos_to_youtube(link: str, videos: list):
    print('start upload videos')
    youtube = pytube.YouTube(link)
    video_date = youtube.publish_date
    description = f'{video_date.day} {months[video_date.month]} {video_date.year}'

    for video in videos:
        await upload_video_to_youtube(video, description)
    
    temp_dir = (videos[0])[1].rsplit('/', 1)[0]
    shutil.rmtree(temp_dir)
    print('end upload videos')


async def upload_video_to_youtube(video, description):
    print(f"** upload video {video[2]}")
    media = MediaFileUpload(video[1], chunksize=-1, resumable=True)

    print(video[2])
    print(description)

    meta = {
        'snippet': {
            'title' : video[2],
            'description' : description
        },
        'status':{
            'privacyStatus': 'private',
            'selfDeclaredMadeForKids': 'false'
        }
    }

    insert_request = get_service_creds().videos().insert(
        part=','.join(meta.keys()),
        body=meta,
        media_body=media
    )

    r = resumable_upload(insert_request)
    print(r)


def resumable_upload(request):
  response = None
  error = None
  retry = 0
  while response is None:
    try:
      print('Uploading file...')
      status, response = request.next_chunk()
      if response is not None:
        if 'id' in response:
          print('Video id "%s" was successfully uploaded.' % response['id'])
        else:
          exit('The upload failed with an unexpected response: %s' % response)
    except HttpError as e:
      if  e.resp.status in RETRIABLE_STATUS_CODES:
        error = 'A retriable HTTP error %d occurred:\n%s' % (e.resp.status,
                                                             e.content)
      else:
        raise
    except RETRIABLE_EXCEPTIONS as e:
      error = 'A retriable error occurred: %s' % e

    if error is not None:
      print(error)
      retry += 1
      if retry > MAX_RETRIES:
        exit('No longer attempting to retry.')

      max_sleep = 2 ** retry
      sleep_seconds = random.random() * max_sleep
      print('Sleeping %f seconds and then retrying...' % sleep_seconds)
      time.sleep(sleep_seconds)


async def get_user_info():
    r = get_service().userinfo().get().execute()
    print(json.dumps(r))