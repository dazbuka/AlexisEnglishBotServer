import app.database.requests as rq
from config import logger
import data.user_messages as umsg
from aiogram.types import Message, CallbackQuery
from app.utils.admin_utils import message_answer


# функция отправки медиа пользователю, ответ на колл
async def send_media_to_user_call_with_kb(media,
                                          call : CallbackQuery,
                                          reply_kb,
                                          with_de_tr : bool = None,
                                          added_text: str = None):

    sending_medias = await rq.get_medias_by_filters(media_id=media.id)
    sending_media = sending_medias[0] if len(sending_medias) else None

    if sending_media.media_type=='text':
        message_text = f'{sending_media.caption}\n\n' if sending_media.caption else ''
        message_text += f'Collocation: <b>{sending_media.collocation}</b>'
        if with_de_tr:
            message_text+=(f'\n\n<b>{sending_media.word.word}</b> - {sending_media.word.definition}'
                           f'\n\n<b>{sending_media.word.word}</b> - {sending_media.word.translation}')
        if added_text:
            message_text+=added_text
        bot_mess = await call.message.answer(text = message_text,
                                                 reply_markup = reply_kb)
        bot_mess_num = bot_mess.message_id

    elif sending_media.media_type=='photo':
        message_text = f'{sending_media.caption}\n\n' if sending_media.caption else ''
        message_text += f'Collocation: <b>{sending_media.collocation}</b>'
        if with_de_tr:
            message_text+=(f'\n\n<b>{sending_media.word.word}</b> - {sending_media.word.definition}'
                           f'\n\n<b>{sending_media.word.word}</b> - {sending_media.word.translation}')
        if added_text:
            message_text+=added_text
        bot_mess = await call.message.answer_photo(photo = sending_media.telegram_id,
                                                       caption = message_text,
                                                       reply_markup = reply_kb)
        bot_mess_num = bot_mess.message_id
    elif sending_media.media_type == 'video':
        message_text = f'{sending_media.caption}\n\n' if sending_media.caption else ''
        message_text += f'Collocation: <b>{sending_media.collocation}</b>'
        if with_de_tr:
            message_text += (f'\n\n<b>{sending_media.word.word}</b> - {sending_media.word.definition}'
                             f'\n\n<b>{sending_media.word.word}</b> - {sending_media.word.translation}')
        if added_text:
            message_text += added_text
        bot_mess = await call.message.answer_video(video=sending_media.telegram_id,
                                                       caption=message_text,
                                                       reply_markup=reply_kb)
        bot_mess_num = bot_mess.message_id

    else:
        text = 'Неизвестный формат media, обратитесь к администратору'
        bot_mess_num = await message_answer(source=call, message_text=text, reply_kb=reply_kb)

        logger.info(f'Неизвестный формат media {sending_media.media_type}, id: {sending_media.id}')


    await rq.update_user_last_message_id(user_tg_id=call.from_user.id, message_id=bot_mess_num)


# функция отправки теста пользователю, ответ на колл
async def send_test_to_user_with_kb(media, call : CallbackQuery, reply_kb):
    if media.media_type=='test4':
        text = umsg.USER_STUDYING_TEST4_TASK_MESSAGE + '\n' + media.collocation
    elif media.media_type == 'test7':
        words = await rq.get_words_by_filters(word_id=media.word_id)
        word = words[0].word
        text = f'{umsg.USER_STUDYING_TEST7_TASK_MESSAGE}\n<b>{word}</b>'
    else:
        text = f'Неизвестный формат теста, обратитесь к администратору'
    # await call.message.answer(text=text, reply_markup=reply_kb)
    bot_mess_num = await message_answer(source=call, message_text=text, reply_markup=reply_kb)
    await rq.update_user_last_message_id(user_tg_id=call.from_user.id, message_id=bot_mess_num)


# проверка ответа на тест
async def check_user_test_answer(media, message : Message, reply_kb):
    answer=message.text.lower()
    if media.media_type == 'test4':
        word_dict = await rq.get_words_by_filters(word_id=media.word_id)
        word = word_dict[0].word
        if len(answer) >= 3 and answer in word :
            message_text = umsg.USER_STUDYING_TEST_ANSWER_RIGHT_WORD.format(word, answer)
        else:
            message_text = umsg.USER_STUDYING_TEST_CHECK_YOURSELF.format(word, answer)
    elif media.media_type == 'test7':
        medias = await rq.get_medias_by_filters(word_id=media.word_id, media_only=True)
        # вводим переменную - количество правильно введенных коллокаций
        score = 0
        # выводим список возможных коллокаций, имеющихся в базе данных и если совпадает с ответом - увеличиваем счет
        rezult = []
        for media in medias:
            rezult.append(media.collocation)
            if media.collocation in answer:
                score += 1
        right_answer = '\n'.join(map(str,rezult))
        message_text = f'{umsg.USER_STUDYING_TEST_CHECK_YOURSELF.format(right_answer, message.text)}'
        # если есть совпадения - дописываем счет
        if score != 0:
            message_text = f"🎉Good job, your score: {score}\n\n{message_text}"
    else:
        message_text = f'Неизвестный формат теста, обратитесь к администратору'
        print('unknown test format')

    bot_mess_num = await message_answer(source=message, message_text=message_text, reply_markup=reply_kb)
    await rq.update_user_last_message_id(user_tg_id=message.from_user.id, message_id=bot_mess_num)






