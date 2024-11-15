import { IContextBot } from "@models/context.interface";
import { Middleware } from "telegraf";
import * as dotenv from 'dotenv'

dotenv.config()

const { ALLOWED_USERS } = process.env;

const authorizationMiddleware: Middleware<IContextBot> = async (ctx, next) => {
  if (ALLOWED_USERS == undefined || ALLOWED_USERS.includes(ctx.chat?.id?.toString() ?? '')) {
    return await next();
  } {
    await ctx.deleteMessage(ctx.message?.message_id);
    return ctx.sendMessage('🤡');
  }
};
export default authorizationMiddleware;