import json
import os
import re

import pytube
from youtubesearchpython import *
from moviepy.editor import *
import datetime
 
from app.config_reader import load_config

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

API_KEY = '*********'
 
APP_TOKEN_FILE = "app/helpers/client_secret.json"
USER_TOKEN_FILE = "user_token.json"

SCOPES = [
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/userinfo.email'
]

async def get_creds_saved():
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

async def get_service():
    creds = get_creds_saved()
    service = build('oauth2', 'v2', credentials=creds)
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

async def download_video(url: str):
    youtube = pytube.YouTube(url)
    youtube_temp = 'cut_video_temp' + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    video = youtube.streams.filter(res='1080p', file_extension='mp4').first().download(f'app/temp/{youtube_temp}')
    return (video.rsplit('\\', 1)[1], youtube_temp)

async def parse_timestamp_to_seconds(time: str):
    if len(time.split(':')) == 2:
        t = datetime.datetime.strptime(time, '%M:%S')
        return t.minute * 60 + t.second
    if len(time.split(':')) == 3:
        t = datetime.datetime.strptime(time, '%H:%M:%S')
        return t.hour * 3600 + t.minute * 60 + t.second

async def cut_video(link: str, clips: list):
    video = await download_video(link)
    cut_clips_path = []

    with VideoFileClip(f'app/temp/{video[1]}/{video[0]}') as stream_video:
        for clip in clips:
            t1 = await parse_timestamp_to_seconds(clip[0])
            t2 = await parse_timestamp_to_seconds(clip[1])
            cut_clip = stream_video.subclip(t1, t2)
            cut_clip_path = f'app/temp/{video[1]}/{clip[2]}.mp4'
            cut_clips_path.append(cut_clip_path)
            cut_clip.write_videofile(cut_clip_path)

    return cut_clips_path

async def upload_video():
    return None

async def get_user_info(channel_id = 'UCFBNtfaEW8gbHK-76rePSpA'):
    r = get_service().userinfo().get().execute()
    print(json.dumps(r))