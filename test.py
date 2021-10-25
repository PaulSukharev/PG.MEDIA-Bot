from PIL import Image, ImageFont, ImageDraw
# from youtubecrawler.synced import crawl
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
          "октября",
          "НОЯБРЯ",
          "ДЕКАБРЯ"]

title_font = ImageFont.truetype('SolomonSans.ttf', 75)

my_image = Image.open("ishod.jpg")
W, H = my_image.size
image_editable = ImageDraw.Draw(my_image)

now = (datetime.now())
day = (now.day)
month = (months[now.month])
year = (now.year)

title_text = "Кузнецов Игорь"

title_date = f'{day} {month} {year}'

w, h = title_font.getsize(title_text)
image_editable.text(((W-w)/2, 210), title_text, (255, 255, 255), font=title_font)

w, h = title_font.getsize(title_date)
image_editable.text(((W-w)/2, 1080), title_date, (255, 255, 255), font=title_font)

my_image.save("result_test.jpg")