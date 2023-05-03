from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton


inline_kb = InlineKeyboardMarkup(row_width=2)
ikb1 = InlineKeyboardButton("Использовать ✅", callback_data="use")
ikb2 = InlineKeyboardButton("Другое описание ➡️", callback_data="another")
inline_kb.add(ikb1, ikb2)


def create_search_inline(user_id: int) -> InlineKeyboardMarkup:
    search_inline = InlineKeyboardMarkup(row_width=2)
    new_ikb1 = InlineKeyboardButton("❤️", callback_data=f'like:{user_id}')
    new_ikb2 = InlineKeyboardButton("👎", callback_data=f'dislike:{user_id}')
    search_inline.add(new_ikb1, new_ikb2)
    return search_inline


look_inline = InlineKeyboardMarkup(row_width=1)
look_inline.add(InlineKeyboardButton("Посмотреть анкету", callback_data="look"))


def create_link_inline(text: str, url: str) -> InlineKeyboardMarkup:
    message_inline = InlineKeyboardMarkup(row_width=1)
    message_inline.add(InlineKeyboardButton(text, url=url))
    return message_inline

def triple_keyboard(value1, value2, value3):
    triple_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    triple_kb.add(value1, value2).add(value3)
    return triple_kb


def double_keyboard(value1, value2):
    double_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    double_kb.add(value1, value2)
    return double_kb


def keyboard(value):
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(value)
    return kb
