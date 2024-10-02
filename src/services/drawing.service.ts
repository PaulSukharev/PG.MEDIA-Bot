
import { createCanvas, loadImage, registerFont } from "canvas";
import fs from 'fs';
import moment from "moment";

const months = ["ЯНВАРЯ", "ФЕВРАЛЯ", "МАРТА", "АПРЕЛЯ", "МАЯ", "ИЮНЯ", "ИЮЛЯ", "АВГУСТА", "СЕНТЯБРЯ", "ОКТЯБРЯ", "НОЯБРЯ", "ДЕКАБРЯ"];


export async function drawLivePicture(title: string | undefined, date: moment.Moment): Promise<string> {
    const liveImg = await loadImage(__dirname + '/../assets/img/live.jpg');

    return new Promise((resolve, rejects) => {
        if (title == undefined || title == '') {
            throw Error('Title is empty');
        }
    
        title = title.toUpperCase();

        registerFont(__dirname + '/../assets/fonts/SolomonSans-Medium.ttf',  {
            family: 'SolomonSans Medium'
        });
    
        const canvas = createCanvas(liveImg.width, liveImg.height);
        const ctx = canvas.getContext("2d");
        ctx.drawImage(liveImg, 0, 0);
    
        ctx.font = '60px "SolomonSans Medium"';
        let td = ctx.measureText(title);
        const tw = td.width;
    
        const x = Math.floor((liveImg.naturalWidth - tw) / 2);
    
        ctx.fillStyle = "rgb(255, 255, 255)";
        ctx.fillText(title, x, 255);
    
        const dateStr = `${date.date()} ${months[date.month()]} ${date.year()}`;
        td = ctx.measureText(dateStr);
        const xDate = Math.floor((liveImg.naturalWidth - td.width) / 2);
    
        ctx.fillStyle = "rgb(0, 0, 0)";
        ctx.fillText(dateStr, xDate, 1200);
        
        const path = __dirname + '/../../temp/' + title + '.jpeg';
        const out = fs.createWriteStream(path),
        stream = canvas.createJPEGStream();
        stream.pipe(out);
        out.on("finish", () => {
            console.log("Done");
            resolve(path);
        });
    });
}

export async function drawSermonPicture1(title: string | undefined, date: moment.Moment, picture_path: string) {
    const liveImg = await loadImage(picture_path);

    return new Promise((resolve, rejects) => {
        if (title == undefined || title == '') {
            throw Error('Title is empty');
        }
    
        title = title.toUpperCase();

        registerFont(__dirname + '/../assets/fonts/SolomonSans-Medium.ttf',  {
            family: 'SolomonSans Medium'
        });
    
        const canvas = createCanvas(liveImg.width, liveImg.height);
        const ctx = canvas.getContext("2d");
        ctx.drawImage(liveImg, 0, 0);
    
        ctx.font = '60px "SolomonSans Medium"';
        let td = ctx.measureText(title);
        const tw = td.width;
    
        const x = Math.floor((liveImg.naturalWidth - tw) / 2);
    
        ctx.fillStyle = "rgb(255, 255, 255)";
        ctx.fillText(title, x, 255);
    
        const dateStr = `${date.date()} ${months[date.month()]} ${date.year()}`;
        td = ctx.measureText(dateStr);
        const xDate = Math.floor((liveImg.naturalWidth - td.width) / 2);
    
        ctx.fillStyle = "rgb(0, 0, 0)";
        ctx.fillText(dateStr, xDate, 1200);
        
        const path = __dirname + '/../../temp/' + title + '.jpeg';
        const out = fs.createWriteStream(path),
        stream = canvas.createJPEGStream();
        stream.pipe(out);
        out.on("finish", () => {
            console.log("Done");
            resolve(path);
        });
    });
}

// export async function drawSermonPicture(preacher: string, title: string, date: moment.Moment, picture_path: string, transparent: number) {
//     const my_image = await loadImage(picture_path);

//     W, H = my_image.size
//     ratio = W / H
//     if ratio > 16/9:
//         crop_width = H * 16 / 9
//         crop_heigth = H
//     else:
//         crop_heigth = W * 9 / 16
//         crop_width = W

//     im_crop = my_image.crop(((W - crop_width) // 2, (H - crop_heigth) // 2, (W + crop_width) // 2, (H + crop_heigth) // 2))
//     new_im = im_crop.resize((1920, 1080), Image.ANTIALIAS)

//     enhancer = ImageEnhance.Brightness(new_im)
//     dark_im = enhancer.enhance(transparent)

//     front_im = Image.open('src/img/preach.png')
//     front_im = front_im.convert('RGBA')

//     dark_im.paste(front_im, (0, 0), front_im)

//     W, H = dark_im.size
//     image_editable = ImageDraw.Draw(dark_im)

//     title_lines = len(title.split('\n'))
// }
