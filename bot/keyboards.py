from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_gender_keyboard():
    
    btn_male = KeyboardButton(text="Мужской")
    btn_female = KeyboardButton(text="Женский")


    keyboard = ReplyKeyboardMarkup(
        keyboard=[ 
            [btn_male],
            [btn_female]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def get_swipe_keyboard(user_id):
    
    btn_like = InlineKeyboardButton(text="❤️", callback_data=f"like_{user_id}")
    btn_dislike = InlineKeyboardButton(text="👎", callback_data=f"dislike_{user_id}")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [btn_like, btn_dislike]
        ]
    )
    return keyboard



def get_main_menu_keyboard():
    btn_search_profiles = KeyboardButton(text="Моя анкета")
    btn_profile = KeyboardButton(text="Изменить анкету")
    btn_edit = KeyboardButton(text="Искать анкету")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [btn_search_profiles],
            [btn_profile],
            [btn_edit]
        ],
        resize_keyboard=True
    )
    return keyboard