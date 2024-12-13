import { IContextBot } from "@models/context.interface";

export async function sendTempMessage(ctx: IContextBot, text: string, prevMsg?: number): Promise<number> {
    if (prevMsg) {
        await ctx.deleteMessage(prevMsg);
    }
    return new Promise<number>((resolve, reject) => {
        ctx.sendMessage(text).then(res => resolve(res.message_id));
    })
}
