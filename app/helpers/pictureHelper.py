from turtle import width
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from sympy import factor
from youtubesearchpython import *
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


def get_picture_ishod(preacher, title, date):
    my_image = Image.open("src/img/ishod.jpg")
    W, H = my_image.size
    image_editable = ImageDraw.Draw(my_image)
    title_font = ImageFont.truetype('src/fonts/SolomonSans-Medium.ttf', 75, encoding='UTF-8')

    preacher = preacher.encode().replace(b'\xb8\xcc\x86', b'\xb9').decode()
    print(preacher)
    w, h = title_font.getsize(preacher)
    image_editable.text(((W-w)/2, 225), preacher, (255, 255, 255), font=title_font)

    w, h = title_font.getsize(date)
    image_editable.text(((W-w)/2, 1080), date, (255, 255, 255), font=title_font)

    title_font = ImageFont.truetype('src/fonts/SolomonSans-SemiBold.ttf', 150, encoding='UTF-8')
    w, h = title_font.getsize(title)
    image_editable.text(((W-w)/2, (H-h)/2), title, (255, 255, 255), font=title_font)
    picture = f'{title} {datetime.now().strftime("%Y%m%d-%H%M%S")}.jpg'
    my_image.save(picture, quality=100)
    return os.path.abspath(picture)


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

    date = datetime.strptime(date, '%d.%m.%Y').date()
    date = f'{date.day} {months[date.month].lower()} {date.year}'
    w, h = preacher_font.getsize(date)
    image_editable.text(((W-w)/2, 850), date, (255, 255, 255), font=preacher_font)

    temp_dir = picture_path.rsplit('/', 1)[0]
    pict_title = title.split('\n')[0]
    picture = f'{temp_dir}/{pict_title} {datetime.now().strftime("%Y%m%d-%H%M%S")}.png'

    print(picture)
    # dark_im = dark_im.convert('RGB')
    dark_im.save(picture, quality=100)
    return os.path.abspath(picture)


def get_picture_from_link(link):
    video_info = YoutubeHelper.get_video_info(link)['items'][0]
    print(video_info)
    video_info_snippet = video_info['snippet']
    video_title = video_info_snippet['title'].split('|')
    title_text = video_title[0].strip()
    if re.search(r'богослужение', title_text):
        result = get_picture_trans(title_text, video_title[1].strip())
        YoutubeHelper.upload_thumbnail(video_info['id'], result)
        return result

    if re.search(r'Исход', title_text):
        result = get_picture_ishod(video_title[1].strip(), video_title[0].strip(), video_info_snippet['description'].strip())
        YoutubeHelper.upload_thumbnail(video_info['id'], result)
        return result

    # if re.search(r'Церковь на Поклонной Горе', video_info['channel']['name']):
    #     return None

    return None


def get_picture_from_title(title, date):
    video_title = title.split('|')
    title_text = video_title[0].strip()

    if re.search(r'богослужение', title_text):
        result = get_picture_trans(title_text, video_title[1].strip())
        return result

    if re.search(r'Исход', title_text):
        result = get_picture_ishod(video_title[1].strip(), video_title[0].strip(), date.strip())
        return result

    return None
