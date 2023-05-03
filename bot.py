from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from src.keyboards.keyboard_for_users import triple_keyboard, keyboard
from src.config import TelegramBot
from src.states.register import register_form
from src.states.update_photo import register_new_photo
from src.states.delete_user_from_db import register_deleting_form
from src.states.update_description import register_new_description
from src.states.searching_forms import register_search
from src.database.main_database import db

bot = Bot(token=TelegramBot.token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot=bot, storage=MemoryStorage())
register_form(dp=dp)  # функция регистрации пользователя
register_new_description(dp=dp)  # функция обновления описания
register_deleting_form(dp=dp)  # функция удаления анкеты
register_new_photo(dp=dp)  # функция обновления фотографии
register_search(dp=dp)  # функция подбора анкет


async def on_startup(_):
    """Функция для создания таблиц"""
    db.create_table()
    db.create_matching_table()
    print("Бот запустился!")


@dp.message_handler(commands=['start'])
@dp.message_handler(Text(equals="Помощь", ignore_case=True))
async def process_start(message: types.Message):
    """Функция обработчик на команды /start, Помощь"""
    await message.answer(f"Добро пожаловать, "
                         f"{message.from_user.username if message.from_user.username is not None else 'дорогой друг'}"
                         f" ❤️!\n\n" 
                         f"Всего за <i>несколько простых шагов</i> Вы "
                         f"можете создать и зарегистрировать свой собственный <b>уникальный</b>"
                         f" профиль пользователя 🐼 \n\n"
                         f"Этот бот также предлагает возможность просматривать профили других"
                         f" пользователей, что делает его отличным способом общаться с другими людьми и устанавливать"
                         f" новые связи! По всем вопросам Вы можете обратиться"
                         f" к <a href='https://t.me/xquisite_corpse'>создателю</a> этого бота"
                         f"\n\nЗарегистрируйся прямо сейчас ⬇️",
                         reply_markup=keyboard("Пройти регистрацию"), disable_web_page_preview=True)


@dp.message_handler(Text(equals="Главное меню", ignore_case=True))
async def main_menu(message: types.Message):
    """Функция для вывода главного меню"""
    await message.answer("Вы в главном меню", reply_markup=triple_keyboard("Моя анкета", "Поиск анкет", "Помощь"))


@dp.message_handler(Text(equals="Обновить анкету", ignore_case=True))
async def update_users_form(message: types.Message):
    """Функция для обновления анкеты"""
    if db.check_users_existence(message.from_user.id):  # если пользователь есть в базе данных
        await message.answer("Что желаете обновить?",  # то у него появляется возможность обновить анкету
                             reply_markup=triple_keyboard("Описание", "Фотографию", "Моя анкета"))
    else:
        await message.answer("Для начала зарегистрируйтесь", reply_markup=keyboard("Пройти регистрацию"))


@dp.message_handler(Text(equals="Моя анкета", ignore_case=True))
async def update_all_users_form(message: types.Message):
    """Функция для показа анкеты пользователя"""
    if db.check_users_existence(message.from_user.id):  # если пользователь есть в базе данных
        for photo in db.printout_users_form(message.from_user.id):  # пробегаем по массиву его данных
            await bot.send_photo(message.from_user.id,
                                 photo=photo[6],  # высылаем фото
                                 caption=f"{photo[2]}, {photo[3]} лет\n\n{photo[5]}",  # заголовок
                                 reply_markup=triple_keyboard("Обновить анкету", "Удалить анкету", "Главное меню")
                                 )
    else:
        await message.answer("Для начала зарегистрируйтесь", reply_markup=keyboard("Пройти регистрацию"))


@dp.message_handler()  # хендлер, обрабатывающий другие входящие сообщения
async def empty_handler(message: types.Message):
    await message.reply("Я вас не понимаю. Переходите в главное меню.", reply_markup=keyboard("Главное меню"))


if __name__ == '__main__':
    try:
        executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
    except (KeyboardInterrupt, SystemExit) as ex:
        print("Bot has stopped.")
