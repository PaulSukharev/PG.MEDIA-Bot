import { BaseScene } from "telegraf/scenes";
import { IContextBot } from "../../models/context.interface";
import { isYouTubeVideo } from "@services/youtube.service";
import { addMsgToRemoveList, removeTempMessages } from "utils/processMessages";

const start = new BaseScene<IContextBot>('start');

start.enter(async (ctx) => {
    addMsgToRemoveList(ctx.message?.message_id, ctx);
    removeTempMessages(ctx);

    ctx.session.customText = undefined;
    ctx.session.timestamps = undefined;
    ctx.session.usersList = undefined;
    ctx.session.video = undefined;

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

    try {
        const res = await isYouTubeVideo(ctx.text);
        if (res) {
            await ctx.scene.enter('youtube');
            return;
        }
    } catch (error) {
        console.log(error);
    }
});

start.on('message', async (ctx) => {
    addMsgToRemoveList(ctx.message?.message_id, ctx);

    try {
        const res = await isYouTubeVideo(ctx.text);
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