from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from datetime import *
import re
import os

import helpers.youtubeHelper as YoutubeHelper

months = ["Unknown", "ЯНВАРЯ", "ФЕВРАЛЯ", "МАРТА", "АПРЕЛЯ", "МАЯ", "ИЮНЯ", "ИЮЛЯ", "АВГУСТА", "СЕНТЯБРЯ", "ОКТЯБРЯ", "НОЯБРЯ", "ДЕКАБРЯ"]

class Picture():
    picture_path: str
    title: str
    date: str
    preacher: str
    video_id: str
    result_picture_path: str


def get_picture(title_text):
    my_image = Image.open("src/img/trans.jpg")
    W, H = my_image.size
    image_editable = ImageDraw.Draw(my_image)
    title_font = ImageFont.truetype('src/fonts/SolomonSans-Medium.ttf', 60)

    now = (datetime.now())
    day = (now.day)
    month = (months[now.month])
    year = (now.year)

    title_date = f'{day} {month} {year}'

    w, h = title_font.getsize(title_text)
    image_editable.text(((W-w)/2, 210), title_text, (255, 255, 255), font=title_font)

    w, h = title_font.getsize(title_date)
    image_editable.text(((W-w)/2, 1155), title_date, (0, 0, 0), font=title_font)

    picture = f'{title_text} {datetime.now().strftime("%Y%m%d-%H%M%S")}.jpg'
    my_image.save(picture, quality=100)
    return os.path.abspath(picture)


def get_picture_trans(title, date):
    my_image = Image.open("src/img/trans.jpg")
    W, H = my_image.size
    image_editable = ImageDraw.Draw(my_image)
    title_font = ImageFont.truetype('src/fonts/SolomonSans-Medium.ttf', 60, encoding='UTF-8')

    title = title.upper()
    w, h = title_font.getsize(title)
    image_editable.text(((W-w)/2, 210), title, (255, 255, 255), font=title_font)

    print(date)
    date = datetime.strptime(date, '%d.%m.%Y').date()
    date = f'{date.day} {months[date.month]} {date.year}'
    w, h = title_font.getsize(date)
    image_editable.text(((W-w)/2, 1155), date, (0, 0, 0), font=title_font)

    picture = f'{title} {datetime.now().strftime("%Y%m%d-%H%M%S")}.jpg'
    my_image.save(picture, quality=100)
    return os.path.abspath(picture)

def check_title_length(title):
    title_font = ImageFont.truetype('src/fonts/SolomonSans-SemiBold.ttf', 95, encoding='UTF-8')
    title = title.encode().replace(b'\xb8\xcc\x86', b'\xb9').decode()
    w, h = title_font.getsize_multiline(title, spacing=50)

    return w < 1800

def get_picture_preaching(preacher, title, date, picture_path, transparent):
    my_image = Image.open(picture_path)
    W, H = my_image.size
    ratio = W / H
    if ratio > 16/9:
        crop_width = H * 16 / 9
        crop_heigth = H
    else:
        crop_heigth = W * 9 / 16
        crop_width = W

    im_crop = my_image.crop(((W - crop_width) // 2, (H - crop_heigth) // 2, (W + crop_width) // 2, (H + crop_heigth) // 2))
    new_im = im_crop.resize((1920, 1080), Image.ANTIALIAS)

    enhancer = ImageEnhance.Brightness(new_im)
    dark_im = enhancer.enhance(transparent)

    front_im = Image.open('src/img/preach.png')
    front_im = front_im.convert('RGBA')

    dark_im.paste(front_im, (0, 0), front_im)

    W, H = dark_im.size
    image_editable = ImageDraw.Draw(dark_im)

    title_lines = len(title.split('\n'))

    if (title_lines == 1):
        title_font = ImageFont.truetype('src/fonts/SolomonSans-SemiBold.ttf', 95, encoding='UTF-8')

    if (title_lines == 2):
        title_font = ImageFont.truetype('src/fonts/SolomonSans-SemiBold.ttf', 90, encoding='UTF-8')
    
    title = title.encode().replace(b'\xb8\xcc\x86', b'\xb9').decode()
    w, h = title_font.getsize_multiline(title, spacing=50)
    image_editable.multiline_text(((W-w)/2, (H-h)/2), title, (255, 255, 255), font=title_font, spacing=50, align='center')

    preacher_font = ImageFont.truetype('src/fonts/SolomonSans-Medium.ttf', 60, encoding='UTF-8')

    preacher = preacher.encode().replace(b'\xb8\xcc\x86', b'\xb9').decode()
    w, h = preacher_font.getsize(preacher)
    image_editable.text(((W-w)/2, 180), preacher, (255, 255, 255), font=preacher_font)

    # date = datetime.strptime(date, '%d.%m.%Y').date()
    # date = f'{date.day} {months[date.month].lower()} {date.year}'
    w, h = preacher_font.getsize(date)
    image_editable.text(((W-w)/2, 850), date, (255, 255, 255), font=preacher_font)

    temp_dir = picture_path.rsplit('/', 1)[0]
    pict_title = picture_path.rsplit('/', 1)[1].split('.')[0]
    picture = f'{temp_dir}/{pict_title} {datetime.now().strftime("%Y%m%d-%H%M%S")}.png'

    print(picture)
    # dark_im = dark_im.convert('RGB')
    dark_im.save(picture, quality=100)

    return os.path.abspath(picture)

def get_picture_luke(preacher, title, date):
    luke_path = "src/img/luke.jpg"
    result = get_picture_preaching(preacher, title, date, luke_path, 0.7)
    return result

def get_picture_from_link(link):
    video_info = YoutubeHelper.get_video_info(link)['items'][0]
    video_info_snippet = video_info['snippet']

    video_title = video_info_snippet['title'].strip()
    video_description = video_info_snippet['description'].strip()

    picture_path = get_picture_from_title(video_title, video_description)

    if picture_path:
        YoutubeHelper.upload_thumbnail(video_info['id'], picture_path)

    return picture_path


def get_picture_from_title(title, date):
    video_title = title.split('|')
    title_text = video_title[0].strip()

    if re.search(r'богослужение', title_text):
        result = get_picture_trans(title_text, video_title[1].strip())
        return result

    if re.search(r'Луки', title_text):
        result = get_picture_luke(video_title[1].strip(), video_title[0].strip(), date.strip())
        return result
    
    result = get_picture_preaching(video_title[1].strip(), video_title[0].strip(), date.strip())

    return None

def get_picture_type(title: str):
    # 0 - трансляция
    # 1 - луки
    # 2 - выбрать вручную

    if re.search(r'богослужение', title):
        return 0
    
    if re.search(r'Луки', title):
        return 1

    return 2

def get_picture_info(link: str):
    video_info = YoutubeHelper.get_video_info(link)['items'][0]
    video_info_snippet = video_info['snippet']
    print(video_info_snippet)
    video_title = video_info_snippet['title'].strip()
    title_text = video_title.split('|')[0].strip()
    preacher = video_title.split('|')[1].strip()
    video_description = video_info_snippet['description'].strip()
    video_id = video_info['id']

    picture_type = get_picture_type(title_text)

    return [picture_type, preacher, title_text, video_description, video_id]

def compress_under_size(size, file_path):
    '''file_path is a string to the file to be custom compressed
    and the size is the maximum size in bytes it can be which this 
    function searches until it achieves an approximate supremum'''

    quality = 100 #not the best value as this usually increases size

    current_size = os.stat(file_path).st_size

    while current_size > size or quality == 0:
        if quality == 0:
            os.remove(file_path)
            print("Error: File cannot be compressed below this size")
            break

        current_size = compress_pic(file_path, quality)
        # current_size = os.stat(file_path).st_size
        quality -= 5


def compress_pic(file_path, qual):
    '''File path is a string to the file to be compressed and
    quality is the quality to be compressed down to'''
    picture = Image.open(file_path)
    dim = picture.size

    picture.save(file_path,"JPEG", optimize=True, quality=qual) 

    processed_size = os.stat(file_path).st_size

    return processed_size

