import { Markup } from "telegraf";
import { BaseScene } from "telegraf/scenes";
import { IContextBot } from "../../models/context.interface";
import { downloadAndUploadVideo, getVideo } from "@services/youtube.service";
import { addMsgToRemoveList, removeTempMessages } from "utils/processMessages";
import { Timestamp } from "@models/video";

const scene = new BaseScene<IContextBot>('youtube');

scene.enter(async (ctx) => {
    ctx.session.video = await getVideo(ctx.text!);

    const keyboard = [];

    if (ctx.session.video.timestamps?.length > 0) {
        keyboard.push(['вырезать отрывок']);
    } else {
        keyboard.push(['скачать аудио']);
    }

    if (keyboard.length > 0) {
        keyboard.push(['сделать картинку']);
    } else {
        await ctx.scene.enter('youtube.picture');
        return;
    }

    const msg = await ctx.reply('что делаем?', {
        reply_markup: {
            keyboard: keyboard,
            resize_keyboard: true,
            one_time_keyboard: true
        }
    });

    addMsgToRemoveList(msg.message_id, ctx);
});

scene.on('message', async (ctx) => {
    addMsgToRemoveList(ctx.message.message_id, ctx);

    switch (ctx.text) {
        case 'сделать картинку':
            await ctx.scene.enter('youtube.picture');
            break;
        case 'вырезать отрывок':
            const keyboard = getTimestampsKeyboard(ctx.session.video?.timestamps!);

            const msg = await ctx.reply('выбери что-нибудь:', {
                reply_markup: {
                    inline_keyboard: keyboard,
                    resize_keyboard: true
                }
            });

            addMsgToRemoveList(msg.message_id, ctx);

            break;
        case 'скачать аудио':
            await ctx.scene.enter('youtube.audio');
            break;
        default:
            break;
    }
});

scene.action(/timestamp\:(\d*)$/, ctx => {
    const timestamp = ctx.session.video?.timestamps?.find(x => x.start.toString() == ctx.match[1]);

    if (!timestamp) {
        return;
    }
    timestamp.select = !timestamp.select;

    const keyboard = getTimestampsKeyboard(ctx.session.video?.timestamps ?? [])
    ctx.editMessageReplyMarkup({inline_keyboard: keyboard})
});

scene.action('готово', async ctx => {
    await ctx.editMessageText('⏳', {
        reply_markup: undefined
    });
    removeTempMessages(ctx);

    const msg = await ctx.sendMessage('⏳');
    addMsgToRemoveList(msg.message_id, ctx);

    downloadAndUploadVideo(ctx.session.video?.id, ctx.session.video?.timestamps?.filter(x => x.select), ctx).subscribe(() => {
        const msg = ctx.session.video?.timestamps?.filter(x => x.select).map(x => x.title).join(', ');
        ctx.reply(`🟢 Видео: ${msg}`);

        ctx.scene.enter('start');
    });
});

const getTimestampsKeyboard = (timestamps: Timestamp[]) => {
    const keyboard = timestamps.map(x => [ Markup.button.callback((x.select ? '✅' : '❌') + ' ' + x.title, 'timestamp:' + x.start.toString())]);
    keyboard.push([ Markup.button.callback('готово', 'готово')]);
    return keyboard;
}

export default scene;