import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = '7205371569:AAGM4zv59yX3-9Z9MJhMY9T7Vzwdc6iutMQ'
SUPPORT_CHAT_ID = -1002831062931
SUPPORT_ACCOUNT_ID = 8222462689
WELCOME_IMAGE_PATH = 'welcome_image.png'
USER_TRACKING_TOPIC_ID = None  # ID темы для отслеживания пользователей (будет создана автоматически)

# Словарь для хранения связи пользователь -> тема
user_topics = {}

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветственное сообщение с картинкой и кнопками"""
    user = update.effective_user
    first_name = user.first_name or "друг"
    
    # Логирование пользователя в отдельную тему
    await log_user_start(context, user)
    
    message_text = (
        f"Здравствуйте, {first_name}! Добро пожаловать в магазин украшений для магнитотерапии LUXTONE. "
        f"Мы создаём стильные украшения с магнитами, которые идеальны для ежедневного использования и станут "
        f"отличным подарком для близких. LUXTON — международная компания, сотрудничающая с клиниками и медицинскими "
        f"центрами. Наши изделия подлежат обязательной сертифицикации и рекомендуются врачами как дополнение к лечению.\n\n"
        f"Кликните на кнопку ниже, для перехода в нужный раздел⬇️"
    )
    
    # Создание инлайн-кнопок
    keyboard = [
        [InlineKeyboardButton("Дополнительные звенья", callback_data="additional_links")],
        [InlineKeyboardButton("Задать вопрос", callback_data="ask_question")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправка сообщения с картинкой
    try:
        with open(WELCOME_IMAGE_PATH, 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=message_text,
                reply_markup=reply_markup
            )
    except FileNotFoundError:
        logger.warning(f"Файл {WELCOME_IMAGE_PATH} не найден, отправляю текст без картинки")
        await update.message.reply_text(message_text, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Ошибка при отправке картинки: {e}, отправляю текст")
        await update.message.reply_text(message_text, reply_markup=reply_markup)

async def log_user_start(context, user):
    """Логирует информацию о пользователе в отдельную тему"""
    global USER_TRACKING_TOPIC_ID
    
    try:
        # Создаем тему для отслеживания, если еще не создана
        if USER_TRACKING_TOPIC_ID is None:
            try:
                topic = await context.bot.create_forum_topic(
                    chat_id=SUPPORT_CHAT_ID,
                    name="📊 Статистика пользователей"
                )
                USER_TRACKING_TOPIC_ID = topic.message_thread_id
                logger.info(f"Создана тема для статистики с ID: {USER_TRACKING_TOPIC_ID}")
            except Exception as e:
                logger.error(f"Ошибка при создании темы статистики: {e}")
                return
        
        # Отправляем информацию о пользователе
        username_text = f"@{user.username}" if user.username else "Нет username"
        user_info = (
            f"🆕 Новый запуск бота\n\n"
            f"👤 Имя: {user.first_name} {user.last_name or ''}\n"
            f"🔗 Username: {username_text}\n"
            f"🆔 Telegram ID: {user.id}"
        )
        
        await context.bot.send_message(
            chat_id=SUPPORT_CHAT_ID,
            message_thread_id=USER_TRACKING_TOPIC_ID,
            text=user_info
        )
    except Exception as e:
        logger.error(f"Ошибка при логировании пользователя: {e}")

# Обработчик нажатий на инлайн-кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает нажатия на инлайн-кнопки"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    username = user.username or user.first_name or f"User_{user.id}"
    
    if query.data == "additional_links":
        topic_name = f"Доп звенья {username}"
        await create_topic_and_start_dialog(query, context, user, topic_name, "дополнительных звеньев")
    
    elif query.data == "ask_question":
        topic_name = f"Вопрос от {username}"
        await create_topic_and_start_dialog(query, context, user, topic_name, "вашего вопроса")

async def create_topic_and_start_dialog(query, context, user, topic_name, dialog_type):
    """Создает тему в группе и начинает диалог"""
    try:
        # Создание темы в группе
        topic = await context.bot.create_forum_topic(
            chat_id=SUPPORT_CHAT_ID,
            name=topic_name
        )
        
        # Сохранение связи пользователь -> тема
        user_topics[user.id] = {
            'topic_id': topic.message_thread_id,
            'topic_name': topic_name
        }
        
        # Уведомление в группе
        await context.bot.send_message(
            chat_id=SUPPORT_CHAT_ID,
            message_thread_id=topic.message_thread_id,
            text=f"Новый запрос от пользователя @{user.username or user.first_name} (ID: {user.id})"
        )
        
        # Уведомление пользователю (без картинки)
        await query.message.reply_text(
            text="Благодарим за обращение! Ожидайте, скоро с вами свяжется наш специалист поддержки."
        )
        
        logger.info(f"Создана тема '{topic_name}' для пользователя {user.id}")
        
    except Exception as e:
        logger.error(f"Ошибка при создании темы: {e}")
        await query.message.reply_text(
            text="Произошла ошибка. Пожалуйста, попробуйте позже или свяжитесь с нами напрямую @luxtonstore"
        )

# Обработчик сообщений от пользователей
async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пересылает сообщения пользователя в соответствующую тему группы"""
    user = update.effective_user
    
    if user.id in user_topics:
        topic_info = user_topics[user.id]
        try:
            # Пересылка сообщения в тему группы
            await context.bot.send_message(
                chat_id=SUPPORT_CHAT_ID,
                message_thread_id=topic_info['topic_id'],
                text=f"От @{user.username or user.first_name}:\n\n{update.message.text}"
            )
            await update.message.reply_text("Ваше сообщение отправлено. Ожидайте ответа.")
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения в группу: {e}")
            await update.message.reply_text("Ошибка отправки. Попробуйте позже.")
    else:
        await update.message.reply_text("Пожалуйста, сначала выберите раздел через команду /start")

# Обработчик сообщений из группы (ответы от поддержки)
async def handle_support_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пересылает ответы из группы пользователю"""
    if update.message.chat.id == SUPPORT_CHAT_ID and update.message.message_thread_id:
        # Находим пользователя по topic_id
        for user_id, topic_info in user_topics.items():
            if topic_info['topic_id'] == update.message.message_thread_id:
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"Ответ от поддержки:\n\n{update.message.text}"
                    )
                    logger.info(f"Ответ отправлен пользователю {user_id}")
                except Exception as e:
                    logger.error(f"Ошибка при отправке ответа пользователю {user_id}: {e}")
                break

def main():
    """Запуск бота"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, 
        handle_user_message
    ))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.Chat(SUPPORT_CHAT_ID),
        handle_support_message
    ))
    
    # Запуск бота
    logger.info('LUXTON бот запущен...')
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
