import { Telegraf, session } from "telegraf";
import * as dotenv from 'dotenv'
import stage from "./scences";
import { IContextBot } from "./models/context.interface";
import { getPictureTypes, uploadToYoutube } from "@services/youtube.service";
import { drawLivePicture } from "@services/drawing.service";
import { addMsgToRemoveList } from "utils/processMessages";

dotenv.config()

const { BOT_TOKEN } = process.env;
if (!BOT_TOKEN) throw new Error('"BOT_TOKEN" env var is required!');
const bot = new Telegraf<IContextBot>(BOT_TOKEN);

bot.use(session());
bot.use(stage.middleware())

bot.start(ctx => ctx.scene.enter('start'));

bot.on('message', async (ctx) => {
    if (ctx.scene.current?.id == undefined) {
        await ctx.scene.enter('start');
    };
});

bot.launch();