from telethon import TelegramClient
from .strings import (
    scan_approved_string,
    bot_gban_string,
    proof_string,
    forced_scan_string,
)
from Skynet_System import (
    Skynet_logs,
    Skynet_approved_logs,
    GBAN_MSG_LOGS,
    BOT_TOKEN,
    API_ID_KEY,
    API_HASH_KEY,
)
from Skynet_System.plugins.Mongo_DB.gbans import update_gban, delete_gban


class SkynetClient(TelegramClient):
    """SkynetClient - Subclass of Telegram Client."""

    def __init__(self, *args, **kwargs):
        """Declare stuff."""
        self.gban_logs = GBAN_MSG_LOGS
        self.approved_logs = Skynet_approved_logs
        self.log = Skynet_logs
        self.bot = None
        self.processing = 0
        self.processed = 0
        if BOT_TOKEN:
            self.bot = TelegramClient(
                "SkynetSystem", api_id=API_ID_KEY, api_hash=API_HASH_KEY
            ).start(bot_token=BOT_TOKEN)
        super().__init__(*args, **kwargs)

    async def gban(
        self,
        enforcer=None,
        target=None,
        reason=None,
        msg_id=None,
        approved_by=None,
        auto=False,
        bot=False,
        message=False,
    ) -> bool:
        """Gbans & Fbans user."""
        if self.gban_logs:
            logs = self.gban_logs
        else:
            logs = self.log
        if not auto:
            await self.send_message(
                logs,
                f"/gban [{target}](tg://user?id={target}) {reason} // By {enforcer} | #{msg_id}",
            )
            await self.send_message(
                logs,
                f"/fban [{target}](tg://user?id={target}) {reason} // By {enforcer} | #{msg_id}",
            )
        else:
            await self.send_message(
                logs,
                f"/gban [{target}](tg://user?id={target}) Auto Gban[${msg_id}] {reason}",
            )
            await self.send_message(
                logs,
                f"/fban [{target}](tg://user?id={target}) Auto Gban[${msg_id}] {reason}",
            )
        if bot:
            await self.send_message(
                Skynet_approved_logs,
                bot_gban_string.format(enforcer=enforcer, scam=target, reason=reason),
            )
        else:
            await self.send_message(
                Skynet_approved_logs,
                scan_approved_string.format(
                    enforcer=enforcer, scam=target, reason=reason, proof_id=msg_id
                ),
            )
        if not target:
            return False
        await update_gban(
            victim=int(target),
            reason=reason,
            proof_id=int(msg_id),
            enforcer=int(enforcer),
            message=message,
        )

    async def ungban(self, target: int = None, reason: str = None) -> bool:
        if self.gban_logs:
            logs = self.gban_logs
        else:
            logs = self.log
        if not (await delete_gban(target)):
            return False
        await self.send_message(
            logs, f"/ungban [{target}](tg://user?id={target}) {reason}"
        )
        await self.send_message(
            logs, f"/unfban [{target}](tg://user?id={target}) {reason}"
        )
        return True
