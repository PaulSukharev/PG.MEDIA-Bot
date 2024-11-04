import { IContextBot } from "@models/context.interface";
import { downloadAudio } from "@services/youtube.service";
import { BaseScene } from "telegraf/scenes";
import { addMsgToRemoveList, removeTempMessages } from "utils/processMessages";
import fs from 'fs';
import { Input } from "telegraf";

const scene = new BaseScene<IContextBot>('youtube.audio');

scene.enter(async (ctx) => {
    addMsgToRemoveList(ctx.message?.message_id, ctx);
    removeTempMessages(ctx);

    if (ctx.session.video == undefined) {
        await ctx.scene.enter('start');
        return;
    }

    downloadAudio(ctx.session.video?.id!).subscribe((res) => {
        ctx.sendDocument(Input.fromLocalFile(res)).then(() => {
            if (fs.existsSync(res)) {
                fs.unlinkSync(res);
            }
        });
        ctx.scene.enter('start');
    });
});

export default scene;
