from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ContentType

from app.database.requests import get_medias_by_filters
# import app.utils.admin_utils as aut
from app.keyboards.keyboard_builder import (keyboard_builder, update_button_with_call_item,
                                            update_button_list_with_check)
from app.common_settings import *
from app.utils.admin_utils import (add_item_in_aim_set_plus_minus,
                                   add_item_in_only_one_aim_set, get_new_page_num)
from app.handlers.admin_menu.states.state_params import InputStateParams
from app.keyboards.menu_buttons import button_translation, button_definition, button_repeat_today


class FSMExecutor:
    def __init__(self):
        self.message_text = None
        self.reply_kb = None
        self.media_type = None
        self.media_id = None

    async def execute(self, fsm_state: FSMContext, fsm_call: CallbackQuery = None, fsm_mess: Message = None):
        fsm_state_str = await fsm_state.get_state()
        current_state = fsm_state_str.split(':', 1)[1]
        current_state_params: InputStateParams = await fsm_state.get_value(current_state)
        print(fsm_state_str, end=' -> ')
        next_state_str = current_state_params.next_state.state
        next_state = next_state_str.split(':', 1)[1]
        # зацикливаем для ревижен
        if fsm_state_str == next_state_str:
            next_state_params = current_state_params
        else:
            next_state_params: InputStateParams = await fsm_state.get_value(next_state)
        print(next_state_str)
        # сначала обработчик для колла, заодно проверяем чтобы не было мессаджа
        if fsm_call and not fsm_mess:
            # вытаскиваем колл и убираем из него базовый и добавочный колл (заменяем на пусто)
            item_call = fsm_call.data.replace(current_state_params.call_base, '')
            # самый первый проверочный иф проверяет если текущий стейт - подтверждение всего ввода и будет
            # переход на изменение элементов, в этом случае следуюзий стейт будет преходом, а не цикличиным
            # как обыно, при этом номер страницы мы находим исходя из первого добавленного элемента
            if current_state_params.is_last_state_with_changing_mode:
                print('c1', end='-')
                absolute_next_state = next_state_params
            # если нажата кнопка подтверждения на клавиатуре
            elif CALL_CONFIRM in item_call:
                print('c2', end='-')
                # если список элементов пустой и дальше пропускать нельзя - зацикливаемся в этом же стейте выбора
                # элементов, при этом сообщение меняем на ничего не выбрано туда - обратно
                if not current_state_params.set_of_items and not current_state_params.is_can_be_empty:
                    print('c3', end='-')
                    # выводим сообщение, чередуем, чтобы не было ошибки "невозможно редактировать"
                    common_mess = fsm_call.message.caption if fsm_call.message.caption else fsm_call.message.text
                    print('вот здесь что-то не так')
                    if current_state_params.main_mess in common_mess:
                        current_state_params.main_mess = MESS_NULL_CHOOSING
                    absolute_next_state = current_state_params
                # во всех остальных случаях переходим в следущюий стейт
                else:
                    print('c4', end='-')
                    absolute_next_state = next_state_params
            # если работает каруселька по перемещению между страницами, абсолютный некст будет текущим
            elif any(item_call.startswith(item.value) for item in CarouselButtons):
            # elif (item_call.startswith(CALL_NEXT) or item_call.startswith(CALL_LAST) or
            #         item_call.startswith(CALL_PREV) or item_call.startswith(CALL_FIRST)):
                print('c5', end='-')
                absolute_next_state = current_state_params
            # если не было подтверждения, а была нажата кнопка элемента на клавиатуре не конфирм и не каруселька
            else:
                print('c6', end='-')
                # добавляем элемент в множество выбранных слов и записываем в стейт
                # проверяем может ли быть один - тогда просто симметрично добавляем (это для групп, например)
                # и переходим в следующий стейт, если не может быть один - тогда обновляем просто текущий стейт
                if item_call:
                    if not current_state_params.is_only_one:
                        print('с7', end='-')
                        # добавляем элементы
                        current_state_params.set_of_items = await add_item_in_aim_set_plus_minus(
                                                                aim_set=current_state_params.set_of_items,
                                                                added_item=item_call)
                        absolute_next_state: InputStateParams = current_state_params
                        # и меняем сообщение на добавь еще
                        current_state_params.main_mess = MESS_MORE_CHOOSING
                    # добавляем элемент и в следующий стейт, если нужен только один элемент
                    else:
                        print('с8', end='-')
                        current_state_params.set_of_items = await add_item_in_only_one_aim_set(
                                                                aim_set=current_state_params.set_of_items,
                                                                added_item=item_call)
                        absolute_next_state: InputStateParams = next_state_params
                    # обновляем стейт после добавления элементов
                    await fsm_state.update_data({current_state: current_state_params})


            abs_next_buttons_new = []
            if not absolute_next_state.is_input:
                abs_next_buttons_new = update_button_list_with_check(button_list=absolute_next_state.buttons_pack,
                                                                     call_base=absolute_next_state.call_base,
                                                                     aim_set=absolute_next_state.set_of_items,
                                                                     check=absolute_next_state.buttons_check)

        if fsm_mess and not fsm_call:
            fsm_state_str = await fsm_state.get_state()
            print('m1', end='-')
            # если текущий стейт ждет ввода сообщения
            if current_state_params.is_input:
                print('m2', end='-')
                if fsm_mess.content_type == ContentType.TEXT:
                    added_text = fsm_mess.text.lower()
                    current_state_params.media_type = MediaType.TEXT.value
                    current_state_params.input_text = added_text
                elif fsm_mess.content_type == ContentType.PHOTO:
                    current_state_params.media_type = MediaType.PHOTO.value
                    current_state_params.media_id = fsm_mess.photo[-1].file_id
                    current_state_params.input_text = fsm_mess.caption
                elif fsm_mess.content_type == ContentType.VIDEO:
                    current_state_params.media_type = MediaType.VIDEO.value
                    current_state_params.media_id = fsm_mess.video.file_id
                    current_state_params.input_text = fsm_mess.caption

                await fsm_state.update_data({current_state: current_state_params})

                absolute_next_state : InputStateParams = next_state_params
                abs_next_buttons_new = absolute_next_state.buttons_pack
            # это если мы используем мессаж для поиска среди клавиатуры и остаемся в том же стейте



            # elif not current_state_params.is_input and current_state_params.buttons_kb_list:
            else:
                print('m3', end='-')
                absolute_next_state : InputStateParams = current_state_params

                new_keyboard = []
                for button in absolute_next_state.buttons_pack:
                    if fsm_mess.text.lower() in button.text.lower():
                        new_keyboard.append(button)
                abs_next_buttons_new = new_keyboard
            # этот стейт не должен работать, надо убрать его
            # else:
            #     print('ЕРРОР m4')
            #     absolute_next_state : InputStateParams = next_state_params
            #     abs_next_buttons_new = absolute_next_state.buttons_kb_list
            #     added_item = fsm_mess.text.lower()
            #     current_state_params.input_text = added_item
            #     await fsm_state.update_data({current_state: current_state_params})

            abs_next_buttons_new = update_button_list_with_check(button_list=abs_next_buttons_new,
                                                                 call_base=absolute_next_state.call_base,
                                                                 aim_set=absolute_next_state.set_of_items,
                                                                 check=absolute_next_state.buttons_check)

        page_num = get_new_page_num(call=fsm_call, mess=fsm_mess,
                                    button_list=abs_next_buttons_new,
                                    call_base=absolute_next_state.call_base,
                                    cols=absolute_next_state.buttons_cols,
                                    rows=absolute_next_state.buttons_rows)

        if absolute_next_state.is_media_revision_mode and absolute_next_state.set_of_items:
            media_id = list(absolute_next_state.set_of_items)[0]
            media = await get_medias_by_filters(media_id_new=media_id)
            revision_menu = [[update_button_with_call_item(button_translation, str(media.word_id)),
                              update_button_with_call_item(button_definition, str(media.word_id)),
                              update_button_with_call_item(button_repeat_today, str(media.id))]]

            absolute_next_menu_pack = revision_menu + absolute_next_state.menu_pack
        else:
            absolute_next_menu_pack = absolute_next_state.menu_pack

        print('cm end')

        self.media_type = absolute_next_state.media_type
        self.media_id = absolute_next_state.media_id

        self.message_text = absolute_next_state.main_mess
        self.reply_kb = await keyboard_builder(menu_pack=absolute_next_menu_pack,
                                               buttons_pack=abs_next_buttons_new,
                                               buttons_base_call=absolute_next_state.call_base,
                                               buttons_cols=absolute_next_state.buttons_cols,
                                               buttons_rows=absolute_next_state.buttons_rows,
                                               is_adding_confirm_button=not absolute_next_state.is_only_one,
                                               buttons_page_number=page_num)
        # возвращаемся в тот же стейт добавления слов
        await fsm_state.set_state(absolute_next_state.self_state)



