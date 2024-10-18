
import { Picture, Video } from "@models/video";
import { CanvasRenderingContext2D, createCanvas, loadImage, registerFont } from "canvas";
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

export async function drawSermonPicture(preacher: string, title: string | undefined, date: moment.Moment | string, transparent: number, picture_path: string): Promise<string> {
    const img = await loadImage(picture_path);
    const preach = await loadImage(__dirname + '/../assets/img/preach.png');

    const ratio = img.width / img.height;
    let cropWidth;
    let cropHeigth;

    if (ratio > 16/9) {
        cropWidth = img.height * 16 / 9
        cropHeigth = img.height
    } else {
        cropHeigth = img.width * 9 / 16
        cropWidth = img.width
    }

    return new Promise((resolve, rejects) => {
        if (title == undefined || title == '') {
            throw Error('Title is empty');
        }

        registerFont(__dirname + '/../assets/fonts/SolomonSans-Medium.ttf',  {
            family: 'SolomonSans Medium'
        });

        registerFont(__dirname + '/../assets/fonts/SolomonSans-SemiBold.ttf',  {
            family: 'SolomonSans SemiBold'
        });
    
        const canvas = createCanvas(1920, 1080);
        const ctx = canvas.getContext("2d");
        ctx.drawImage(img, - (img.width - cropWidth) / 2, - (img.height - cropHeigth) / 2);

        ctx.fillStyle = `rgba(0, 0, 0, 0.${transparent})`;
        ctx.fillRect(0, 0, 1920, 1080);
        ctx.drawImage(preach, 0, 0);

        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillStyle = "rgb(255, 255, 255)";

        drawMultilineText(ctx, title);
    
        ctx.fillText(preacher, ctx.canvas.width / 2, 225);
    
        const dateStr = typeof(date) == 'string' ? date : `${date.date()} ${months[date.month()]} ${date.year()}`;
        ctx.fillText(dateStr, ctx.canvas.width / 2, 895);
        
        const path = __dirname + '/../../temp/' + 'test' + '.jpeg';
        const out = fs.createWriteStream(path),
        stream = canvas.createJPEGStream();
        stream.pipe(out);
        out.on("finish", () => {
            console.log("Done");
            resolve(path);
        });
    });
}

export function getPictureFromVideo(video: Video): Picture {
    const title = video.title.split('|')[0].trim();
    let date;
    let preacher;

    if (hasNumber(video.title.split('|')[1])) {
        date = video.title.split('|')[1].trim();
    } else {
        preacher = video.title.split('|')[1].trim();
        date = video.description?.trim();
    }

    return {
        title: title,
        preacher: preacher,
        date: date,
        transparent: 500
    }
}

export async function drawPicture(picture: Picture) {
    return drawSermonPicture(picture.preacher!, picture.title!, picture.date!, picture.transparent!, picture.imagePath!);
}

function drawMultilineText(ctx: CanvasRenderingContext2D, text: string) {
    const titleLines = text.split('\n');
    let font: string;

    if (titleLines.length == 1) {
        font = '95px "SolomonSans SemiBold"';
    } else if (titleLines.length == 2) {
        font = '90px "SolomonSans SemiBold"';
    } else {
        font = '85px "SolomonSans SemiBold"';
    }

    ctx.font = font;
    var approxFontHeight=parseInt(ctx.font);

    let y = Math.floor(ctx.canvas.height / 2 - (approxFontHeight * (titleLines.length - 1)) / 2 + approxFontHeight / 4);

    for (var i = 0; i < titleLines.length; i++) {
        ctx.fillText(titleLines[i], ctx.canvas.width / 2, y + approxFontHeight * i);
    }
}

function hasNumber(myString: string) {
    return /\d/.test(myString);
}

// function drawMultilineText1(ctx: any, text: string, opts: any) {

//     // Default options
//     if (!opts)
//         opts = {}
//     if (!opts.font)
//         opts.font = 'sans-serif'

//     if (!opts.rect)
//         opts.rect = {
//             x: 0,
//             y: 0,
//             width: ctx.canvas.width,
//             height: ctx.canvas.height
//         }
//     if (!opts.lineHeight)
//         opts.lineHeight = 1.1
//     if (!opts.minFontSize)
//         opts.minFontSize = 80
//     if (!opts.maxFontSize)
//         opts.maxFontSize = 95

//     const words = text.split(' ');
//     var lines = []
//     let y;  //New Line

//     // Finds max font size  which can be used to print whole text in opts.rec

    
//     let lastFittingLines;                       // declaring 4 new variables (addressing issue 3)
//     let lastFittingFont;
//     let lastFittingY;
//     let lastFittingLineHeight;
//     for (var fontSize = opts.minFontSize; fontSize <= opts.maxFontSize; fontSize++) {

//         // Line height
//         var lineHeight = fontSize * opts.lineHeight

//         // Set font for testing with measureText()
//         ctx.font = ' ' + fontSize + 'px ' + opts.font

//         // Start
//         var x = opts.rect.x;
//         y = lineHeight; //modified line        // setting to lineHeight as opposed to fontSize (addressing issue 1)
//         lines = []
//         var line = ''

//         // Cycles on words

       
//         for (var word of words) {
//             // Add next word to line
//             var linePlus = line + word + ' '
//             // If added word exceeds rect width...
//             if (ctx.measureText(linePlus).width > (opts.rect.width)) {
//                 // ..."prints" (save) the line without last word
//                 lines.push({ text: line, x: x, y: y })
//                 // New line with ctx last word
//                 line = word + ' '
//                 y += lineHeight
//             } else {
//                 // ...continues appending words
//                 line = linePlus
//             }
//         }

//         // "Print" (save) last line
//         lines.push({ text: line, x: x, y: y })

//         // If bottom of rect is reached then breaks "fontSize" cycle
            
//         if (y > opts.rect.height)                                           
//             break;
            
//         lastFittingLines = lines;               // using 4 new variables for 'step back' (issue 3)
//         lastFittingFont = ctx.font;
//         lastFittingY = y;
//         lastFittingLineHeight = lineHeight;

//     }

//     lines = lastFittingLines;                   // assigning last fitting values (issue 3)                    
//     ctx.font = lastFittingFont;                                                                   

//     const offset = opts.rect.y - lastFittingLineHeight / 2 + (opts.rect.height - lastFittingY) / 2;     // modifying calculation (issue 2)
//     for (var line of lines)
//         // Fill or stroke
//         if (opts.stroke)
//             ctx.strokeText(line.text.trim(), line.x, line.y + offset) //modified line
//         else
//             ctx.fillText(line.text.trim(), line.x, line.y + offset) //modified line

//     // Returns font size
//     return fontSize
// }
