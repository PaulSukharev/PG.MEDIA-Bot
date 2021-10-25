from PIL import Image, ImageFont, ImageDraw
from youtubecrawler import crawl
from datetime import *

months = ["Unknown",
          "ЯНВАРЯ",
          "ФЕВРАЛЯ",
          "МАРТА",
          "АПРЕЛЯ",
          "МАЯ",
          "ИЮНЯ",
          "ИЮЛЯ",
          "АВГУСТА",
          "СЕНТЯБРЯ",
          "ОКТЯБРЯ",
          "НОЯБРЯ",
          "ДЕКАБРЯ"]

title_font = ImageFont.truetype('SolomonSans.ttf', 60)

class Picture: 
    def get_picture(title_text):
        my_image = Image.open("trans.jpg")
        W, H = my_image.size
        image_editable = ImageDraw.Draw(my_image)

        now = (datetime.now())
        day = (now.day)
        month = (months[now.month])
        year = (now.year)

        title_date = f'{day} {month} {year}'

        w, h = title_font.getsize(title_text)
        image_editable.text(((W-w)/2, 210), title_text, (255, 255, 255), font=title_font)

        w, h = title_font.getsize(title_date)
        image_editable.text(((W-w)/2, 1155), title_date, (0, 0, 0), font=title_font)

        my_image.save("result.jpg")
        return 'result.jpg'

    def get_picture_from_link(link):
        yt=crawl(video_link=link)

        title_text=yt.VidTitle()
        title_date=yt.description()

        my_image = Image.open("ishod.jpg")
        W, H = my_image.size
        image_editable = ImageDraw.Draw(my_image)

        now = (datetime.now())
        day = (now.day)
        month = (months[now.month])
        year = (now.year)

        # title_date = f'{day} {month} {year}'

        w, h = title_font.getsize(title_text)
        image_editable.text(((W-w)/2, 210), title_text, (255, 255, 255), font=title_font)

        w, h = title_font.getsize(title_date)
        image_editable.text(((W-w)/2, 1155), title_date, (0, 0, 0), font=title_font)

        my_image.save("result_test.jpg")
        return 'result_test.jpg'   