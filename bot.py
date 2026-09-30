import telebot

# ТОКЕН и ID группы Bothost подставит сам из настроек панели, здесь их менять не нужно!
import os
API_TOKEN = os.getenv('BOT_TOKEN') 
GROUP_ID = os.getenv('GROUP_ID')    

bot = telebot.TeleBot(API_TOKEN)
user_states = {}  # Хранилище имени автора: {chat_id: "Имя"}

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type == 'private':
        bot.send_message(message.chat.id, "Привет! Как тебя подписать в сообщении?")
        user_states[message.chat.id] = {'step': 'get_name'}

@bot.message_handler(func=lambda message: message.chat.type == 'private')
def get_name(message):
    user_id = message.chat.id
    if user_id in user_states and user_states[user_id].get('step') == 'get_name':
        user_states[user_id]['name'] = message.text
        user_states[user_id]['step'] = 'get_media'
        bot.send_message(user_id, f"Принято! Тебя подпишем как: *{message.text}*.\n\nТеперь отправь мне всё что угодно (текст, фото, видео, файл, голосовое), и я перешлю это в группу.")

# Обработчик ВСЕХ типов сообщений (текст, фото, видео, документы и т.д.)
@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker'], func=lambda message: message.chat.type == 'private')
def handle_media(message):
    user_id = message.chat.id
    
    if user_id not in user_states or user_states[user_id].get('step') != 'get_media':
        bot.send_message(user_id, "Сначала нажми /start и укажи свою подпись.")
        return

    name = user_states[user_id]['name']
    caption_text = f"📣 **Сообщение от:** {name}"
    
    try:
        # Если это просто текст
        if message.content_type == 'text':
            final_text = f"{caption_text}\n\n{message.text}"
            bot.send_message(GROUP_ID, final_text, parse_mode='Markdown')
            
        # Если это фото
        elif message.content_type == 'photo':
            # Если пользователь прикрепил к фото свой текст, добавляем его
            if message.caption:
                caption_text += f"\n\n{message.caption}"
            bot.send_photo(GROUP_ID, message.photo[-1].file_id, caption=caption_text, parse_mode='Markdown')
            
        # Если это видео
        elif message.content_type == 'video':
            if message.caption:
                caption_text += f"\n\n{message.caption}"
            bot.send_video(GROUP_ID, message.video.file_id, caption=caption_text, parse_mode='Markdown')
            
        # Если это документ (файл)
        elif message.content_type == 'document':
            if message.caption:
                caption_text += f"\n\n{message.caption}"
            bot.send_document(GROUP_ID, message.document.file_id, caption=caption_text, parse_mode='Markdown')
            
        # Если это аудио или голосовое
        elif message.content_type in ['audio', 'voice']:
            bot.send_message(GROUP_ID, caption_text, parse_mode='Markdown')
            bot.forward_message(GROUP_ID, user_id, message.message_id)
            
        # Если это стикер
        elif message.content_type == 'sticker':
            bot.send_message(GROUP_ID, caption_text, parse_mode='Markdown')
            bot.send_sticker(GROUP_ID, message.sticker.file_id)

        bot.send_message(user_id, "🚀 Успешно отправлено в группу анонимно!")
        
    except Exception as e:
        bot.send_message(user_id, f"❌ Ошибка при отправке. Проверьте, добавлен ли бот в группу.")
    
    # Сбрасываем состояние для возможности отправить новое сообщение
    del user_states[user_id]

bot.infinity_polling()
