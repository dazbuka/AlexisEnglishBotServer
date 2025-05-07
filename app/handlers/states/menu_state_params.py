from app.keyboards.menu_buttons import button_admin_menu
from aiogram.types import InlineKeyboardButton

class MenuStateParams:
    """
    Класс для хранения состояний меню в боте Telegram.
    Содержит данные о текущем состоянии меню: callback-данные кнопки, текущее меню кнопок и основное сообщение.
    """
    def __init__(self,
                 curr_call : str,
                 curr_menu : list[list[InlineKeyboardButton]],
                 curr_main_mess: str):

        self.curr_call = curr_call
        self.curr_menu = curr_menu
        self.curr_main_mess = curr_main_mess

    async def update_with_admin_menu(self):
        self.curr_menu.append([button_admin_menu])

    def __repr__(self):
        return (
            f'- Current Call: {self.curr_call}\n'
            f'- Current Menu:\n{self.curr_menu}\n'
            f'- Main Message: {self.curr_main_mess}'
        )
