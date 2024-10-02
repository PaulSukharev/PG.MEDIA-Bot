import { BaseScene } from "telegraf/scenes";
import { IContextBot } from "../../models/context.interface";
import { getYoutubeVideoId, isYouTubeVideo } from "@services/youtube.service";
import { addMsgToRemoveList, removeMessage, removeTempMessages } from "utils/processMessages";

const start = new BaseScene<IContextBot>('start');

start.start(ctx => ctx.scene.enter('start'));

start.enter(async (ctx) => {
    addMsgToRemoveList(ctx.message?.message_id, ctx);

    removeTempMessages(ctx);

    const msg = await ctx.reply('😬', {
        reply_markup: {
            remove_keyboard: true
        }
    });

    addMsgToRemoveList(msg.message_id, ctx);

    await ctx.telegram.setMyCommands([{
        command: 'start',
        description: '💾 старт'
    }]);
});

start.on('message', async (ctx) => {
    addMsgToRemoveList(ctx.message?.message_id, ctx);

    try {
        const res = await isYouTubeVideo(ctx.text);
        console.log(res);
        if (res) {
            ctx.scene.enter('youtube');
            return;
        }
        const msg = await ctx.reply('🤡');
        addMsgToRemoveList(msg.message_id, ctx);

    } catch (error) {
        console.log(error);
    }
});

export default start;