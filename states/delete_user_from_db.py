from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from src.database.main_database import db
from src.keyboards.keyboard_for_users import double_keyboard, keyboard


class Deleting(StatesGroup):
    delete_users_form = State()


async def process_delete(message: types.Message):
    if db.check_users_existence(message.from_user.id):
        await message.answer("Вы действительно хотите удалить свою анкету?\n"
                             "Для дальнейшего использования вам будет необходимо зарегистрироваться вновь",
                             reply_markup=double_keyboard("Удалить", "Отменить удаление"))
        await Deleting.delete_users_form.set()
    else:
        await message.answer("Вам нечего удалять, вы не зарегистрированы", reply_markup=keyboard("Главное меню"))


async def process_wrong_deleting(message: types.Message):
    await message.reply("Не понимаю вас, используйте приведенную клавиатуру ниже",
                        reply_markup=double_keyboard("Удалить", "Отменить удаление"))
    return


async def process_final_deleting(message: types.Message, state: FSMContext):
    await state.update_data(msg=message.text)
    data = await state.get_data()
    if data['msg'] == "Удалить":
        db.delete_user_form(message.from_user.id)
        await message.reply("Ваша анкета была удалена", reply_markup=keyboard("Пройти регистрацию"))
    else:
        await message.reply("Процесс удаления отменён", reply_markup=keyboard("Главное меню"))
    await state.finish()


def register_deleting_form(dp: Dispatcher):
    dp.register_message_handler(process_delete, Text(equals="Удалить анкету", ignore_case=True))
    dp.register_message_handler(process_wrong_deleting, lambda text: not text.text, state=Deleting.delete_users_form)
    dp.register_message_handler(process_wrong_deleting, lambda msg: msg.text.capitalize() not in ("Удалить", "Отменить удаление"),
                                state=Deleting.delete_users_form)
    dp.register_message_handler(process_final_deleting, state=Deleting.delete_users_form)
