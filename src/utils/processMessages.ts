import { IContextBot } from '@models/context.interface';

export const addMsgToRemoveList = (messageId: number | undefined, ctx: IContextBot) => {
	if (messageId == undefined) {
		return;
	}
	const user = ctx.from!;
	if (!ctx.session.usersList) {
		ctx.session.usersList = [{ ...user, messagesToRemove: [messageId] }];
		return;
	}

	const oldU = ctx.session.usersList.find((u) => u.id === user.id);
	if (!oldU) {
		return;
	}
	const hasMsg = oldU.messagesToRemove.find(x => x === messageId);
	if (hasMsg) {
		return;
	}
	oldU.messagesToRemove.push(messageId);
};

const getMsgToRemoveList = (ctx: IContextBot) => {
	const msgToRemoveList = ctx.session.usersList?.find(
		(u) => u.id === ctx.from?.id
	)?.messagesToRemove;
	return msgToRemoveList ?? [];
};

export const removeMessage = (messageId: number, ctx: IContextBot) => {
	try {
		ctx.deleteMessage(messageId).catch((er) => {});
	} catch (error) {

	}
}

export const removeTempMessages = (ctx: IContextBot) => {
	const msgIdList = getMsgToRemoveList(ctx);
	const chatId = ctx.chat?.id;
	if (msgIdList.length > 0 && chatId) {
		for (const msgId of msgIdList) {
			try {
				ctx.telegram.deleteMessage(chatId, msgId).catch((er) => {});
			} catch (error) {

			}
		}
	}
};