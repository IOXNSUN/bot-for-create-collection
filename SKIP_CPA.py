код был такой:

import json
import logging
import os
import uuid
from telebot import TeleBot, types
import html  # Добавлено

# --- Настройки ---
BOT_TOKEN = "{{token}}"
TMP_DIR = "/tmp/postman_collections"
TEMPLATES_DIR = "/home/**/templates"
# --- Конец настроек ---

# Создаем бота
bot = TeleBot(BOT_TOKEN)
user_states = {}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def escape_html(text):
    """Экранирует HTML-специальные символы."""
    return html.escape(text)

@bot.message_handler(commands=["start"])
def cmd_start(message):
    chat_id = message.chat.id
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("CPA", callback_data="CPA"))
    keyboard.add(types.InlineKeyboardButton("SKIP_CPA", callback_data="SKIP_CPA"))
    bot.send_message(chat_id, "Выберите тип коллекции:", reply_markup=keyboard)
    user_states[chat_id] = {"step": "type"}

@bot.message_handler(commands=["cancel"])
def cmd_cancel(message):
    chat_id = message.chat.id
    user_states.pop(chat_id, None)
    bot.send_message(chat_id, "Операция отменена. Нажмите /start для новой попытки.")

@bot.callback_query_handler(func=lambda call: call.data in ["CPA", "SKIP_CPA"])
def on_type_chosen(call):
    chat_id = message.chat.id
    typ = call.data
    logging.info(f"Выбрали тип {typ}, chat_id = {chat_id}")
    state = user_states.get(chat_id, {})
    state["type"] = typ
    state["step"] = "merchant"
    user_states[chat_id] = state
    bot.send_message(chat_id, "Введите merchant_id:")

@bot.message_handler(func=lambda message: True, content_types=["text"])
def handle_text(message):
    chat_id = message.chat.id
    text = message.text
    state = user_states.get(chat_id, {})

    if state.get("step") == "merchant":
        state["merchant"] = text
        state["step"] = "account"
        user_states[chat_id] = state
        bot.send_message(chat_id, "Введите account_id:")
    elif state.get("step") == "account":
        state["account"] = text
        # готовим файл
        typ = state["type"]
        tpl_name = f"{typ}.postman_collection.json"  # ожидает CPA.postman_collection.json или SKIP_CPA.postman_collection.json
        out_name = f"{chat_id}_{typ}_{uuid.uuid4().hex[:8]}.postman_collection.json"
        out_path = os.path.join(TMP_DIR, out_name)
        try:
create_collection_from_template(tpl_name, state["merchant"], state["account"], out_path)
            with open(out_path, "rb") as doc:
                # Подпись без форматирования, экранируем HTML, если нужно
                caption = f"Коллекция {escape_html(typ)} (merchant_id={escape_html(state['merchant'])}, account_id={escape_html(state['account'])}"
                # Устанавливаем parse_mode=None
                bot.send_document(chat_id, doc, caption=caption, parse_mode=None)
            logging.info(f"Sent collection {out_path} to {chat_id} (type={typ})")
        except FileNotFoundError:
            bot.send_message(chat_id, "Ошибка: шаблон не найден. Убедитесь, что в /home/ioxnsun/bot/postman_bot/templates/SKIP_CPA.postman_collection.json")
            logging.error(f"Template not found: {tpl_name}")
        except Exception as e:
            bot.send_message(chat_id, f"Произошла ошибка: {e}")
            logging.exception("Error building collection")
        finally:
            try:
                os.remove(out_path)
            except Exception:
                pass
            user_states.pop(chat_id, None)
            bot.send_message(chat_id, "Готово. Чтобы создать новую коллекцию, нажмите /start.")
    else:
         bot.send_message(chat_id, "Неизвестная команда. Нажмите /start для начала работы.")

def create_collection_from_template(template_name, merchant_id, account_id, output_path):
    """Создает коллекцию Postman из шаблона, заменяя merchant_id и account_id."""
    template_path = os.path.join(TEMPLATES_DIR, template_name) #  Исправлено TEMPLATE_DIR -> TEMPLATES_DIR
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            collection = json.load(f)
    except FileNotFoundError:
        logging.error(f"Template file not found: {template_path}")
        raise # re-raise the exception

    # Обновляем переменные, если секция "variable" существует
    if "variable" in collection and isinstance(collection["variable"], list):
        for item in collection["variable"]:
            if isinstance(item, dict):
                if item.get("key") == "merch_id":
                    item["value"] = merchant_id
                if item.get("key") == "account_id":
                    item["value"] = account_id

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(collection, f, indent=2, ensure_ascii=False) # ensure_ascii=False для корректной записи русских символов
    except Exception as e:
        logging.exception(f"Error writing to output file: {output_path}")
        raise # re-raise the exception

def ensure_dirs():
    os.makedirs(TMP_DIR, exist_ok=True)
    if not os.path.exists(TEMPLATES_DIR):
        os.makedirs(TEMPLATES_DIR)

if __name__ == "__main__":
    ensure_dirs()
    logging.info("Postman bot started")
    bot.infinity_polling()

