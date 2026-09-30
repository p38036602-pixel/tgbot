mport telebot
from telebot import types

API_TOKEN = 'ВАШ_ТОКЕН_ИЗ_BOTFATHER'
GROUP_ID = -5526648257

bot = telebot.TeleBot(API_TOKEN)
user_states = {}  # Хранилище временных данных пользователей

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type == 'private':
        bot.send_message(message.chat.id, "Привет! Как тебя подписать в сообщении? (Введи имя, ник или 'Аноним')")
        user_states[message.chat.id] = {'step': 'get_name'}

@bot.message_handler(func=lambda message: message.chat.type == 'private')
def handle_private(message):
    user_id = message.chat.id
    
    if user_id not in user_states:
        bot.send_message(user_id, "Нажми /start, чтобы начать заново.")
        return

    state = user_states[user_id]['step']

    if state == 'get_name':
        user_states[user_id]['name'] = message.text
        user_states[user_id]['step'] = 'get_text'
        bot.send_message(user_id, f"Принято! Тебя подпишем как: *{message.text}*.\nТеперь отправь текст сообщения, которое нужно переслать в группу.")
        
    elif state == 'get_text':
        name = user_states[user_id]['name']
        text_to_send = message.text
        
        # Формируем красивый текст для группы
        final_message = f"📣 **Сообщение от:** {name}\n\n{text_to_send}"
        
        try:
            bot.send_message(GROUP_ID, final_message, parse_mode='Markdown')
            bot.send_message(user_id, "🚀 Сообщение успешно отправлено в группу анонимно!")
        except Exception as e:
            bot.send_message(user_id, "❌ Ошибка при отправке. Проверьте, добавлен ли бот в группу.")
            
        # Сбрасываем состояние для следующего сообщения
        del user_states[user_id]

bot.infinity_polling()
