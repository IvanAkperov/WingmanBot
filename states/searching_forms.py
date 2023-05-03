from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from src.database.main_database import db
from src.keyboards.keyboard_for_users import keyboard, triple_keyboard, look_inline, create_link_inline,\
    create_search_inline
from aiogram.types.input_media import InputMediaPhoto
from io import BytesIO


class Searcher(StatesGroup):
    searching = State()


async def process_search(message: types.Message):
    user_id = message.from_user.id
    if db.check_users_existence(user_id):
        await message.answer("Сейчас подберем тебе кого-нибудь", reply_markup=keyboard("Закончить поиск"))
        age = db.get_users_age_gender_partner(user_id)[0]
        gender = db.get_users_age_gender_partner(user_id)[1]
        partner = db.get_users_age_gender_partner(user_id)[2]
        db.create_new_matchings(user_id, age, gender, partner)

        look = db.search(user_id)
        if look is not None:
            await Searcher.searching.set()
            search_inline = create_search_inline(look[0])
            await message.bot.send_photo(user_id, photo=look[6],
                                         caption=f'{look[2]}, {look[3]} лет\n\n{look[5]}',
                                         reply_markup=search_inline)
        else:
            await message.answer("Пока для тебя ничего нет \U0001F614", reply_markup=keyboard("Главное меню"))
    else:
        await message.answer("Для начала необходимо зарегистрироваться", reply_markup=keyboard("Пройти регистрацию"))


async def process_call(call: types.CallbackQuery):
    user_id = call.from_user.id
    like_str, look_id = call.data.split(":")
    if look_id is not None:
        like = False
        if like_str == "like":
            like = True
        elif like_str == "dislike":
            like = False

        user = db.get_users_age_gender_partner(user_id)
        age = user[0]
        gender = user[1]
        partner = user[2]
        db.create_new_matchings(user_id, age, gender, partner)

        db.set_like(user_id, look_id, like)

        if like:
            look_inline.inline_keyboard[0][0].callback_data = f'look:{user_id}'
            await call.bot.send_message(look_id, text="Вы понравились этому человеку!", reply_markup=look_inline)

        if db.is_relationship(user_id, look_id):
            send = db.get_users(user_id)
            look = db.get_users(look_id)

            await call.bot.send_message(look[0], text="У вас возникла связь с этим человеком!")
            keyboard_for_look = create_link_inline("Связаться", f'https://t.me/{send[1]}')
            await call.bot.send_photo(look[0], photo=send[6],
                                      caption=f'{send[2]},{send[3]} лет\n\n{send[5]}',
                                      reply_markup=keyboard_for_look)

            await call.bot.send_message(user_id, text="У вас возникла связь с этим человеком!")
            keyboard_for_send = create_link_inline("Связаться", f'https://t.me/{look[1]}')
            await call.bot.send_photo(user_id, photo=look[6],
                                      caption=f'{look[2]}, {look[3]} лет\n\n{look[5]}',
                                      reply_markup=keyboard_for_send)

        look = db.search(user_id)
        if look is not None:
            photo = InputMediaPhoto(BytesIO(look[6]))
            await call.bot.edit_message_media(media=photo, chat_id=call.message.chat.id, message_id=call.message.message_id)
            search_inline = create_search_inline(look[0])
            await call.bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                caption=f'{look[2]}, {look[3]} лет\n\n{look[5]}',
                                                reply_markup=search_inline)

        else:
            await call.message.answer("На данный момент анкеты закончились.", reply_markup=keyboard("Закончить поиск"))
            await call.message.delete()
    else:
        await call.message.answer("Произошла какая-то ошибка", reply_markup=keyboard("Закончить поиск"))


async def process_look(call: types.CallbackQuery):
    if call.data.split(":")[0] == "look":
        await call.message.answer("Переходим к просмотру", reply_markup=keyboard("Закончить поиск"))
        check_user_id = call.data.split(":")[1]
        look = db.get_users(check_user_id)
        if look is not None:
            await Searcher.searching.set()
            search_inline = create_search_inline(look[0])
            await call.bot.send_photo(call.from_user.id, photo=look[6],
                                         caption=f'{look[2]}, {look[3]} лет\n\n{look[5]}',
                                         reply_markup=search_inline)
        else:
            await call.message.answer("Произошла какая-то ошибка", reply_markup=keyboard("Главное меню"))


async def process_cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("А что заканчивать то?", reply_markup=keyboard("Главное меню"))
        return
    await state.finish()
    await message.answer("Поиск завершён.", reply_markup=triple_keyboard("Моя анкета", "Главное меню", "Помощь"))


def register_search(dp: Dispatcher):
    dp.register_message_handler(process_search, Text(equals="Поиск анкет", ignore_case=True))
    dp.register_callback_query_handler(process_call, lambda call: True, state=Searcher.searching)
    dp.register_callback_query_handler(process_look, lambda call: True)
    dp.register_message_handler(process_cancel, Text(equals="Закончить поиск", ignore_case=True), state="*")
