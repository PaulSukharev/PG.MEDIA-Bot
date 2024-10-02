import { IContextBot } from "@models/context.interface";
import { createLivePicture } from "@services/youtube.service";
import { BaseScene } from "telegraf/scenes";
import { addMsgToRemoveList, removeTempMessages } from "utils/processMessages";

const scene = new BaseScene<IContextBot>('youtube.picture');

scene.enter(async (ctx) => {
    addMsgToRemoveList(ctx.message?.message_id, ctx);
    removeTempMessages(ctx);

    if (ctx.session.video == undefined) {
        await ctx.scene.enter('start');
        return;
    }
    console.log(ctx.session.video?.id!);
    const res = await createLivePicture(ctx.session.video?.id!);
    await ctx.sendMessage(ctx.session.video?.title +  (res ? ' ✅' : ' ❌'));
    await ctx.scene.enter('start');
});

export default scene;
