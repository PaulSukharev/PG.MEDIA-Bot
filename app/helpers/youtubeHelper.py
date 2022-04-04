import json
import os
import time
import random
import http.client as httplib
from urllib.parse import parse_qs, urlparse
import httplib2

from youtubesearchpython import *
from moviepy.editor import *


from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from googleapiclient.http import MediaFileUpload



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

def get_video_info(link):

    if link.startswith(('youtu', 'www')):
        link = 'http://' + link

    query = urlparse(link)

    if 'youtube' in query.hostname:
        if query.path == '/watch':
            video_id = parse_qs(query.query)['v'][0]
        elif query.path.startswith(('/embed/', '/v/')):
            video_id = query.path.split('/')[2]
    elif 'youtu.be' in query.hostname:
        print(query.path[1:])
        video_id = query.path[1:]
    else:
        raise ValueError

    print(video_id)
    list = get_service_creds().videos().list(id = video_id, part = "id, snippet, contentDetails, statistics").execute()
    print(list)

    return list


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


def upload_thumbnail(video_id, file_path):
    if file_path:
        media = MediaFileUpload(file_path)
        get_service_creds().thumbnails().set(
            videoId=video_id,
            media_body=media
        ).execute()

    else:
        print('нет картинки')


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