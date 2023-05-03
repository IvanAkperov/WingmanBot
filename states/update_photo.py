from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from src.database.main_database import db
from src.keyboards.keyboard_for_users import keyboard


class ChangePhoto(StatesGroup):
    new_photo = State()


async def updating(message: types.Message):
    await message.answer("Новая фоточка? Хорошо, присылай", reply_markup=keyboard("Отменить процесс изменения"))
    await ChangePhoto.new_photo.set()


async def process_cancel_update(message: types.Message, state: FSMContext):
    await message.answer("Тогда в другой раз :)", reply_markup=keyboard("Главное меню"))
    await state.finish()


async def bad_new_photo(message: types.Message):
    await message.reply("Разве это фотка? Жду нормальную", reply_markup=keyboard("Отменить процесс изменения"))
    return


async def new_photo_updated(message: types.Message, state: FSMContext):
    await state.update_data(photo=message.photo[0].file_id)
    data = await state.get_data()
    await message.answer("Фото обновлено", reply_markup=keyboard("Главное меню"))
    db.update_user_photo(data['photo'], message.from_user.id)
    await state.finish()


def register_new_photo(dp: Dispatcher):
    dp.register_message_handler(updating, Text(equals="Фотографию", ignore_case=True))
    dp.register_message_handler(process_cancel_update, Text(equals="Отменить процесс изменения", ignore_case=True),
                                state=ChangePhoto.new_photo)
    dp.register_message_handler(bad_new_photo, lambda photo: photo.photo != types.ContentType.PHOTO,
                                state=ChangePhoto.new_photo)
    dp.register_message_handler(new_photo_updated, content_types=['photo'], state=ChangePhoto.new_photo)
