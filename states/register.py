import asyncio
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher, Bot
from aiohttp import ClientSession
from src.database.main_database import db
from aiogram.dispatcher.filters.state import StatesGroup, State
from src.keyboards.keyboard_for_users import double_keyboard, triple_keyboard, keyboard, inline_kb
from src.config import TelegramBot
from src.generator.description_generator import random_desc_for_men, random_desc_for_women
from aiogram.types import ChatActions

bot = Bot(token=TelegramBot.token)


class UserStates(StatesGroup):
    gender = State()
    name = State()
    age = State()
    photo = State()
    description = State()
    look_for = State()


class SetUsername(StatesGroup):
    username = State()


async def process_gender(message: types.Message):
    if not db.check_users_existence(message.from_user.id):
        if message.from_user.username is not None:
            await message.reply("Отлично! Для начала определимся с полом. Кто вы? 👇",
                                reply_markup=triple_keyboard("Парень", "Девушка", "Отменить регистрацию"))
            await UserStates.gender.set()
        else:
            await message.answer("Пожалуйста, для корректной работы установите у себя в настройках <b>username</b>"
                                 " (имя пользователя), чтобы при контакте с другими людьми я смог направлять вашу"
                                 " ссылку этим людям", reply_markup=double_keyboard("Сделано ✅", "Не могу установить 😔"),
                                 parse_mode=types.ParseMode.HTML)
            await SetUsername.username.set()
    else:
        await message.answer("Вы уже зарегистрированы. Переходите в главное меню",
                             reply_markup=keyboard("Главное меню"))


async def process_username(message: types.Message, state: FSMContext):
    if message.text == "Сделано ✅":
        await message.answer("Проверяю...")
        await bot.send_chat_action(message.from_user.id, ChatActions.TYPING)
        await asyncio.sleep(1.5)
        if message.from_user.username is not None:
            await state.finish()
            await process_gender(message=message)
        else:
            await message.answer("Вы не задали имя пользователя",
                                 reply_markup=double_keyboard("Сделано ✅", "Не могу установить 😔"))
    elif message.text == "Не могу установить 😔":
        await message.answer("""Чтобы установить имя пользователя в Telegram, выполните следующие действия:
1. Откройте приложение Telegram и перейдите на страницу своего профиля, нажав на изображение своего профиля в верхнем левом углу.
2. Нажмите на кнопку «Изменить», чтобы внести изменения в свой профиль.
3. Прокрутите вниз до раздела «Имя пользователя» и нажмите на него.
4. Введите имя пользователя, которое хотите использовать. Имена пользователей должны содержать от 5 до 32 символов и могут содержать только буквы, цифры и символы подчеркивания.
5. После того, как вы ввели желаемое имя пользователя, нажмите кнопку «Сохранить», чтобы сохранить изменения.\n\nСейчас
пришлю вам подсказку в формате gif 😉""",
                             reply_markup=double_keyboard('Сделано ✅', 'Не могу установить 😔'))
        with open(r"C:\Users\хэй\PycharmProjects\FilesOrganizer\src\other\animation.gif", "rb") as gif:
            await bot.send_animation(message.from_user.id, gif)
        return


async def process_cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("А чего отменять то?", reply_markup=keyboard("Главное меню"))
        return
    await state.finish()
    await message.reply("Регистрация отменена.", reply_markup=keyboard("Пройти регистрацию"))


async def bad_gender(message: types.Message):
    await message.answer("Не понимаю вас, используйте приведенную ниже клавиатуру",
                         reply_markup=triple_keyboard("Парень", "Девушка", "Отменить регистрацию"))
    return


async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(gender=message.text)
    await message.reply("Супер! Как вас зовут?", reply_markup=keyboard("Отменить регистрацию"))
    await UserStates.next()


async def not_name(message: types.Message):
    await message.answer("Упс...Некорректный ввод имени. Попробуйте еще раз!",
                         reply_markup=keyboard("Отменить регистрацию"))
    return


async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.reply(f"{message.text}, сколько вам лет?", reply_markup=keyboard("Отменить регистрацию"))
    await UserStates.next()


async def not_age(message: types.Message):
    await message.answer("Разве это возраст? Введите, пожалуйста, корректные данные в числовом формате",
                         reply_markup=keyboard("Отменить регистрацию"))
    return


async def wrong_age(message: types.Message):
    await message.answer("Недопустимый возраст", reply_markup=keyboard("Отменить регистрацию"))
    return


async def process_photo(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.reply("Теперь пришлите, пожалуйста, ваше фото. Его будут видеть другие пользователи",
                        reply_markup=keyboard("Отменить регистрацию"))
    await UserStates.next()


async def not_photo(message: types.Message):
    await message.answer("Это не фото", reply_markup=keyboard("Отменить регистрацию"))
    return


async def process_desc(message: types.Message, state: FSMContext):
    async with ClientSession() as session:
        async with session.get(await message.photo[-1].get_url()) as response:
            photo = await response.read()

    await state.update_data(photo=photo)
    await message.reply(
        "Класс! Добавьте описание. Расскажите о себе, буквально в двух-трёх предложениях\n\n"
        "Либо воспользуйтесь генератором описания",
        reply_markup=double_keyboard("Генератор описания", "Отменить регистрацию"))
    await UserStates.next()


async def generate_desc(message: types.Message, state: FSMContext):
    sex = await state.get_data()
    if sex['gender'] == "Парень":
        await message.answer(f"{random_desc_for_men()}\n\nКак вам такое описание?", reply_markup=inline_kb)
    else:
        await message.answer(f"{random_desc_for_women()}\n\nКак вам такое описание?", reply_markup=inline_kb)


async def callback_answer(call: types.CallbackQuery, state: FSMContext):
    sex = await state.get_data()
    if call.data == "use":
        await state.update_data(desc=call.message.text[:-25])
        await call.message.reply("Чудненько! Остался последний вопрос.\nКто ваш будущий собеседник? ⬇️",
                                 reply_markup=triple_keyboard("Парень", "Девушка", "Без разницы"))
        await UserStates.next()
    else:
        if sex['gender'] == "Парень":
            await call.message.edit_text(f"{random_desc_for_men()}\n\nКак вам такое описание?",
                                         reply_markup=inline_kb)
        else:
            await call.message.edit_text(f"{random_desc_for_women()}\n\nКак вам такое описание?",
                                         reply_markup=inline_kb)


async def not_desc(message: types.Message):
    await message.answer("Похоже, что вы пытаетесь отправить не текстовое сообщение. Пришлите, пожалуйста, описание"
                         "в текстовом формате",
                         reply_markup=double_keyboard("Генератор описания", "Отменить регистрацию"))
    return


async def weak_desc(message: types.Message):
    await message.answer("Ну же, опишите себя более красочно!",
                         reply_markup=double_keyboard("Генератор описания", "Отменить регистрацию"))


async def long_desc(message: types.Message):
    await message.answer("Ого-го какое длинное описание, сократите его, пожалуйста",
                         reply_markup=double_keyboard("Генератор описания", "Отменить регистрацию"))


async def process_looking_partner(message: types.Message, state: FSMContext):
    await state.update_data(desc=message.text)
    await message.reply("Чудненько! Остался последний вопрос.\nКто ваш будущий собеседник? ⬇️",
                        reply_markup=triple_keyboard("Парень", "Девушка", "Без разницы"))
    await UserStates.next()


async def process_not_chosen_from_kb(message: types.Message):
    await message.answer("Не понимаю вас, используйте приведенную ниже клавиатуру",
                         reply_markup=triple_keyboard("Парень", "Девушка", "Без разницы"))
    return


async def process_finish(message: types.Message, state: FSMContext):
    await state.update_data(partner=message.text)
    data = await state.get_data()
    await message.answer("Вы успешно зарегистрированы!", reply_markup=keyboard("Главное меню"))
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    username = member.user.username
    db.add_users_info(id=message.from_user.id, username=username, name=data['name'], age=data['age'],
                      gender=data['gender'], photo=data['photo'], desc=data['desc'], partner=data['partner'])
    await state.finish()


def register_form(dp: Dispatcher):
    dp.register_message_handler(process_gender, Text(equals="Пройти регистрацию", ignore_case=True))
    dp.register_message_handler(process_username, Text(contains="Сделано ✅"), state=SetUsername.username)
    dp.register_message_handler(process_username, Text(contains="Не могу установить 😔"), state=SetUsername.username)
    dp.register_message_handler(process_cancel, Text(equals="Отменить регистрацию", ignore_case=True), state="*")
    dp.register_message_handler(bad_gender, lambda gender: gender.text.capitalize() not in ("Парень", "Девушка"),
                                state=UserStates.gender)
    dp.register_message_handler(process_name, state=UserStates.gender)
    dp.register_message_handler(not_name, lambda name: not name.text.isalpha(), state=UserStates.name)
    dp.register_message_handler(process_age, state=UserStates.name)
    dp.register_message_handler(not_age, lambda age: not age.text.isdigit(), state=UserStates.age)
    dp.register_message_handler(wrong_age,
                                lambda invalid_age: int(invalid_age.text) < 10 or int(invalid_age.text) > 100,
                                state=UserStates.age)
    dp.register_message_handler(process_photo, state=UserStates.age)
    dp.register_message_handler(not_photo, lambda msg: not msg.photo, state=UserStates.photo)
    dp.register_message_handler(process_desc, content_types=['photo'], state=UserStates.photo)
    dp.register_message_handler(generate_desc, Text(equals="Генератор описания", ignore_case=True),
                                state=UserStates.description)
    dp.register_callback_query_handler(callback_answer, state=UserStates.description)
    dp.register_message_handler(not_desc, lambda desc: not desc.text, state=UserStates.description)
    dp.register_message_handler(weak_desc, lambda weak: len(weak.text.split()) <= 2, state=UserStates.description)
    dp.register_message_handler(long_desc, lambda long: len(long.text) > 350, state=UserStates.description)
    dp.register_message_handler(process_looking_partner, state=UserStates.description)
    dp.register_message_handler(process_not_chosen_from_kb,
                                lambda partner: partner.text.capitalize() not in ("Парень", "Девушка", "Без разницы"),
                                state=UserStates.look_for)
    dp.register_message_handler(process_finish, state=UserStates.look_for)
