from telethon import TelegramClient
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights

api_id = 23685777
api_hash = "75451c38d63946cfb004bc9a02555081"
channel_username_or_id = "lineagetry"
bot_username = "lineagetrace_demo_123_bot"  # exact getMe username, no @

client = TelegramClient("promote_session", api_id, api_hash)

async def main():
    await client.start()
    rights = ChatAdminRights(
        post_messages=True,
        add_admins=False,
        invite_users=True,
        change_info=False,
    )
    await client(EditAdminRequest(
        channel=channel_username_or_id,
        user_id=bot_username,
        admin_rights=rights,
        rank="bot"
    ))
    print("Bot promoted.")

with client:
    client.loop.run_until_complete(main())