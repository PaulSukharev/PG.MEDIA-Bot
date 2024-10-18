import { IContextBot } from "@models/context.interface";
import { getPictureFromVideo } from "@services/drawing.service";
import { createLivePicture } from "@services/youtube.service";
import { BaseScene } from "telegraf/scenes";
import { addMsgToRemoveList, removeTempMessages } from "utils/processMessages";

const scene = new BaseScene<IContextBot>('youtube.picture');

scene.enter(async (ctx) => {
    addMsgToRemoveList(ctx.message?.message_id, ctx);
    removeTempMessages(ctx);

    console.log('youtube.picture');
    console.log(ctx.session);

    if (ctx.session.video == undefined) {
        await ctx.scene.enter('start');
        return;
    }

    ctx.session.video.picture = getPictureFromVideo(ctx.session.video);

    const keyboard = [['трансляция'], ['проповедь']];

    const msg = await ctx.reply('что делаем?', {
        reply_markup: {
            keyboard: keyboard,
            resize_keyboard: true,
            one_time_keyboard: true
        }
    });

    addMsgToRemoveList(msg.message_id, ctx);

    // console.log(ctx.session.video?.id!);
    // const res = await createLivePicture(ctx.session.video?.id!);
    // await ctx.sendMessage(ctx.session.video?.title +  (res ? ' ✅' : ' ❌'));
    // await ctx.scene.enter('start');
});

scene.on('message', async (ctx) => {
    addMsgToRemoveList(ctx.message.message_id, ctx);

    switch (ctx.text) {
        case 'трансляция':
            const res = await createLivePicture(ctx.session.video?.id!);
            await ctx.sendMessage(ctx.session.video?.title +  (res ? ' ✅' : ' ❌'));
            await ctx.scene.enter('start');
            break;
        case 'проповедь':
            await ctx.scene.enter('youtube.picture.sermon');
            break;
        default:
            break;
    }
});

export default scene;
