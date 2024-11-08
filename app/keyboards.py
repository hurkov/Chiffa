from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Connect to a Group⛓️‍💥')],
    [KeyboardButton(text='Social🧷')]
], resize_keyboard=True, input_field_placeholder="choose a button..")

adder = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Add me to a Group🔗', url="https://t.me/chiff_commander_bot?startgroup=start")]
])

social = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='GitHub🐱', url="https://github.com/hurkov"), InlineKeyboardButton(text='Instagram', url='https://www.instagram.com/hurk0vv?igsh=MTI2cmpnNHV4Z3pveg%3D%3D&utm_source=qr')],
    [InlineKeyboardButton(text='Telegram', url='https://t.me/hurk0v')]], resize_keyboard=True)

privilage = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Bot🦾', callback_data="admp_bot"), InlineKeyboardButton(text='Members📚', callback_data="admp_members")],
    [InlineKeyboardButton(text='Tasker⛓', callback_data="admp_tasker"), InlineKeyboardButton(text='⚔Other', callback_data="admp_other")],
    [InlineKeyboardButton(text='Exit🔙', callback_data="exit")]
], resize_keyboard=True)

admp_bot = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Mailing📬', callback_data="admp_mailing"), InlineKeyboardButton(text='Ad Promo📰', callback_data="admp_promo")],
    [InlineKeyboardButton(text='back🔙', callback_data='admp_back')],
    
], resize_keyboard=True)

promo_options = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Send📬", callback_data="send_promo"), InlineKeyboardButton(text="Stop🛑", callback_data="stop_promo")],
    [InlineKeyboardButton(text="back🔙", callback_data="admp_bot")]
])

stop_promo = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Stop🛑", callback_data="stop_promo")],
    [InlineKeyboardButton(text="back🔙", callback_data="admp_bot")]
])

admp_bk_bot = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='back🔙', callback_data='admp_bot')]], resize_keyboard=True)

admp_members = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Db Export📋', callback_data="db_export"), InlineKeyboardButton(text='Ban List🗒️', callback_data="ban_list")],
    [InlineKeyboardButton(text='back🔙', callback_data='admp_back'), InlineKeyboardButton(text='Boost Member🔝', callback_data="boost_mem")]
], resize_keyboard=True)

admp_booster = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Boost📈', callback_data="boost"), InlineKeyboardButton(text='Demote📉', callback_data='demote')],
    [InlineKeyboardButton(text='back🔙', callback_data='admp_members')]
])

admp_bk_members = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='back🔙', callback_data='admp_members')],
], resize_keyboard=True)

admp_tasker = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Trello📋', callback_data="trello")],
    [InlineKeyboardButton(text='back🔙', callback_data='bk_tasker')]
], resize_keyboard=True)

trello = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='connect🔌', callback_data="trello_connect"), 
     InlineKeyboardButton(text='disconnect⛓️‍💥', callback_data="trello_disconnect")],
    [InlineKeyboardButton(text='back🔙', callback_data='admp_tasker')]
])

admp_other = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🦾Bot', callback_data="admp_bot"), InlineKeyboardButton(text='📚Members', callback_data="admp_members")],
    [InlineKeyboardButton(text='⛓Tasker', callback_data="admp_tasker"), InlineKeyboardButton(text='⚔Other', callback_data="admp_other")]
], resize_keyboard=True)