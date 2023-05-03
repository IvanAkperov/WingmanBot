import os


class TelegramBot:
    admin_id: int = 197646514,
    token: str = os.getenv("TOKEN")
    database = "infobase.db"
