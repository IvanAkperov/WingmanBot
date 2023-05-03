from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from src.database.main_database import db
from src.keyboards.keyboard_for_users import keyboard


class UpdateDesc(StatesGroup):
    new_desk = State()


async def new_desk(message: types.Message):
    await message.answer("Появились новые события в жизни? Пора об этом рассказать! Пришли новое описание 😎",
                         reply_markup=keyboard("Отменить процесс изменения"))
    await UpdateDesc.new_desk.set()


async def process_cancelling_update(message: types.Message, state: FSMContext):
    await message.answer("В другой раз тогда!", reply_markup=keyboard("Главное меню"))
    await state.finish()


async def bad_new_desk(message: types.Message):
    await message.reply("Что-то не тянет на текст, пришлите описание в текстовом формате.",
                        reply_markup=keyboard("Отменить процесс изменения"))
    return


async def weak_desc(message: types.Message):
    await message.answer("Ну же, опишите себя более красочно!", reply_markup=keyboard("Отменить процесс изменения"))


async def long_desc(message: types.Message):
    await message.answer("Ого-го какое длинное описание! Сократите его, пожалуйста",
                         reply_markup=keyboard("Отменить процесс изменения"))


async def set_new_desk(message: types.Message, state: FSMContext):
    await state.update_data(new_desc=message.text)
    data = await state.get_data()
    db.update_user_desc(user_desc=data['new_desc'], user_id=message.from_user.id)
    await message.reply("Описание успешно изменено!", reply_markup=keyboard("Главное меню"))
    await state.finish()


def register_new_description(dp: Dispatcher):
    dp.register_message_handler(new_desk, Text(equals="Описание", ignore_case=True))
    dp.register_message_handler(process_cancelling_update, Text(equals="Отменить процесс изменения", ignore_case=True),
                                state=UpdateDesc.new_desk)
    dp.register_message_handler(bad_new_desk, lambda msg: not msg.text, state=UpdateDesc.new_desk)
    dp.register_message_handler(weak_desc, lambda weak: len(weak.text.split()) < 3, state=UpdateDesc.new_desk)
    dp.register_message_handler(long_desc, lambda long: len(long.text) > 350, state=UpdateDesc.new_desk)
    dp.register_message_handler(set_new_desk, state=UpdateDesc.new_desk)
