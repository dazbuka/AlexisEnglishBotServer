from typing import Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.keyboards.menu_buttons import button_confirm
from app.handlers.common_settings import *

def update_button_with_call_base(button : InlineKeyboardButton, call_base : str) -> InlineKeyboardButton:
    button_with_call_base = InlineKeyboardButton(text=button.text,
                                                 callback_data=call_base + button.callback_data)
    return button_with_call_base

def update_button_with_tasks_num(button : InlineKeyboardButton, tasks_num : int) -> InlineKeyboardButton:
    if tasks_num > 0:
        button_with_call_base = InlineKeyboardButton(text=f'{button.text} ({tasks_num})',
                                                     callback_data=button.callback_data)
    else:
        button_with_call_base = InlineKeyboardButton(text=f'{button.text} (no tasks)',
                                                     callback_data=button.callback_data)
    return button_with_call_base

def update_button_with_check(button : InlineKeyboardButton, check : str) -> InlineKeyboardButton:
    button = InlineKeyboardButton(text=f'{check}{button.text}{check}', callback_data=button.callback_data)
    return button

def update_button_with_call_item(button : InlineKeyboardButton, call_item : str) -> InlineKeyboardButton:
    button_with_call_base = InlineKeyboardButton(text=button.text,
                                                 callback_data=button.callback_data + call_item)
    return button_with_call_base

# inline keyboard adding task by schema
async def keyboard_builder(menu_pack : list[list[InlineKeyboardButton]],
                           buttons_base_call : str | None = '',
                           buttons_pack : Optional[list[InlineKeyboardButton]] = None,
                           buttons_cols: int | None = None,
                           buttons_rows: int | None = None,
                           is_adding_confirm_button : bool = False,
                           buttons_page_number: int | None = 0) -> InlineKeyboardMarkup:

    # билдер и массив аджастинга для начала пустой
    builder = InlineKeyboardBuilder()
    adjusting = []
    # если есть параметр добавления в меню списка слов - добавление соответствующих кнопок

    if buttons_pack:
        tables = []
        tables_of_buttons = []
        while buttons_pack:
            table = []
            table_of_buttons = []
            row = 0
            while row < buttons_rows and buttons_pack:
                line = 0
                while line < buttons_cols and buttons_pack:
                    line += 1
                    table_of_buttons.append(buttons_pack[0])
                    buttons_pack = buttons_pack[1:]
                table.append(line)
                row += 1
            tables.append(table)
            tables_of_buttons.append(table_of_buttons)

        for button in tables_of_buttons[buttons_page_number]:
            # ограничение длины колбека - 64, ,возьмем 15 - точно хватит для цифр и начала букв
            builder.add(button)

        if len(tables)>1:
            tables[buttons_page_number].append(4)
            builder.button(text=CarouselButtons.FIRST.value,
                           callback_data=f'{buttons_base_call}{CarouselButtons.FIRST.value}{buttons_page_number}')
            builder.button(text=CarouselButtons.PREV.value,
                           callback_data=f'{buttons_base_call}{CarouselButtons.PREV.value}{buttons_page_number}')
            builder.button(text=CarouselButtons.NEXT.value,
                           callback_data=f'{buttons_base_call}{CarouselButtons.NEXT.value}{buttons_page_number}')
            builder.button(text=CarouselButtons.LAST.value,
                           callback_data=f'{buttons_base_call}{CarouselButtons.LAST.value}{buttons_page_number}')
        adjusting.extend(tables[buttons_page_number])

        # for button in buttons_add_buttons:
        #     builder.add(button)

    # если нужно добавить кнопку подтверждения ввода
    if is_adding_confirm_button:
        builder.add(update_button_with_call_base(button_confirm, buttons_base_call))
        adjusting.append(1)


    # добавляем меню
    for menu_line in menu_pack:
        for menu_item in menu_line:
            builder.add(menu_item)
        adjusting.append(len(menu_line))
    # распределяем меню
    builder.adjust(*adjusting)
    return builder.as_markup()
