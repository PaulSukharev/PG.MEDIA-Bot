import { IContextBot } from "@models/context.interface";
import { uploadThumbnail } from "@services/youtube.service";
import { Input, Markup } from "telegraf";
import { BaseScene } from "telegraf/scenes";
import { addMsgToRemoveList, removeTempMessages } from "utils/processMessages";
import fs from 'fs';
import path from "path";
import axios from "axios";
import { drawPicture } from "@services/drawing.service";

const scene = new BaseScene<IContextBot>('youtube.picture.sermon');

const keyboard = Markup.inlineKeyboard([
    [
        Markup.button.callback("Темнее", "dark"),Markup.button.callback("Светлее", "light")
    ],
    [
        Markup.button.callback("Редактировать название", "title")
    ],
    [
        Markup.button.callback("Скачать", "download"),  Markup.button.callback("Загрузить на Youtube", "upload")
    ]
]);

scene.enter(async (ctx) => {
    addMsgToRemoveList(ctx.message?.message_id, ctx);
    removeTempMessages(ctx);

    const title = ctx.session.video?.title;
    if (title?.includes('Луки')) {
    
        ctx.session.video!.picture!.imagePath = path.resolve('src/assets/img/luke.jpg');
        ctx.session.video!.picture!.transparent = 300;

        const newPic = await drawPicture(ctx.session?.video?.picture!) as string;
        await uploadThumbnail(ctx.session?.video?.id!, newPic);
        await ctx.sendMessage('🟢 Картинка: ' + ctx.session.video?.title);
    
        fs.unlinkSync(newPic);
    
        ctx.scene.enter('start');
        return;
    }

    if (title?.includes('Деяния')) {
        ctx.session.video!.picture!.imagePath! = path.resolve('src/assets/img/acts.jpg');

        const newPic = await drawPicture(ctx.session?.video?.picture!) as string;
        await uploadThumbnail(ctx.session?.video?.id!, newPic);
        await ctx.sendMessage('🟢 Картинка: ' + ctx.session.video?.title);
    
        fs.unlinkSync(newPic);
    
        ctx.scene.enter('start');
        return;
    }

    const msg = await ctx.reply('скинь картинку файлом для обложки', {
        reply_markup: {
            inline_keyboard: [],
            resize_keyboard: true
        }
    });
    addMsgToRemoveList(msg.message_id, ctx);
});

scene.on('document', async (ctx) => {
    addMsgToRemoveList(ctx.message.message_id, ctx);

    const {file_id: fileId, file_name: fileName} = ctx.update.message.document;
    const link = await ctx.telegram.getFileLink(fileId);

    const __tempDir = path.resolve('temp/');
    const filePath = path.resolve(__tempDir, fileName!);
    ctx.session.video!.picture!.imagePath = filePath;

    const writer = fs.createWriteStream(filePath);
    await axios.get(link.toString(), { responseType: "stream" })
        .then((response) => {
            return new Promise((resolve, reject) => {
                response.data.pipe(writer);
                writer.on("error", (err) => {
                    writer.close();
                    reject(err);
                });
                writer.on("close", () => {
                    resolve(true);
                });
            });
        });

    const newPic = await drawPicture(ctx.session!.video!.picture!) as string;
    const msg = await ctx.sendPhoto(Input.fromLocalFile(newPic), keyboard);

    addMsgToRemoveList(msg.message_id, ctx);
});

scene.action('dark', async ctx => {
    removeTempMessages(ctx);

    ctx.session.video!.picture!.transparent! += 100;

    const newPic = await drawPicture(ctx.session!.video!.picture!) as string;
    const msg = await ctx.sendPhoto(Input.fromLocalFile(newPic), keyboard);

    addMsgToRemoveList(msg.message_id, ctx);
});

scene.action('light', async ctx => {
    removeTempMessages(ctx);

    ctx.session.video!.picture!.transparent! -= 100;

    const newPic = await drawPicture(ctx.session!.video!.picture!) as string;
    const msg = await ctx.sendPhoto(Input.fromLocalFile(newPic), keyboard);

    addMsgToRemoveList(msg.message_id, ctx);
});

scene.action('title', async ctx => {
    removeTempMessages(ctx);

    const msg1 = await ctx.sendMessage(ctx.session.video?.picture?.title!);
    addMsgToRemoveList(msg1.message_id, ctx);
    const msg2 = await ctx.sendMessage('Введите новое название');
    addMsgToRemoveList(msg2.message_id, ctx);
});

scene.on('message', async ctx => {
    removeTempMessages(ctx);

    ctx.session.video!.picture!.title = ctx.text;

    const newPic = await drawPicture(ctx.session?.video?.picture!) as string;
    const msg = await ctx.sendPhoto(Input.fromLocalFile(newPic), keyboard);

    addMsgToRemoveList(msg.message_id, ctx);
});

scene.action('download', async ctx => {
    removeTempMessages(ctx);

    const newPic = await drawPicture(ctx.session?.video?.picture!) as string;
    await ctx.sendDocument(Input.fromLocalFile(newPic));

    if (fs.existsSync(ctx.session.video?.picture?.imagePath!)) {
        fs.unlinkSync(ctx.session.video?.picture?.imagePath!);
    }

    ctx.scene.enter('start');
});

scene.action('upload', async ctx => {
    removeTempMessages(ctx);

    const newPic = await drawPicture(ctx.session?.video?.picture!) as string;
    await uploadThumbnail(ctx.session?.video?.id!, newPic);
    await ctx.sendMessage('🟢 Картинка: ' + ctx.session.video?.title);

    fs.unlinkSync(newPic);
    fs.unlinkSync(ctx.session.video?.picture?.imagePath!);

    ctx.scene.enter('start');
});

export default scene;
