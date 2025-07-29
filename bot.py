
import json
import datetime
from aiogram import Bot, Dispatcher, executor, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import os

TOKEN = "8002116184:AAHtPEZX08V33fzxxH8BRVvnhJWaCE42g0Y"

CONFIG_FILE = "config.json"
EMPLOYEES_FILE = "employees.json"

if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        CHAT_ID = data.get("CHAT_ID")
else:
    CHAT_ID = None

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()

def load_employees():
    if not os.path.exists(EMPLOYEES_FILE):
        return []
    with open(EMPLOYEES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_employees(data):
    with open(EMPLOYEES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_chat_id(chat_id):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"CHAT_ID": chat_id}, f, ensure_ascii=False, indent=2)

async def check_birthdays():
    if not CHAT_ID:
        return
    today = datetime.datetime.now().strftime("%d-%m")
    employees = load_employees()
    for emp in employees:
        if emp["birthday"] == today:
            msg = f"🎉 Сегодня день рождения у {emp['name']}! Поздравляем! 🎂"
            await bot.send_message(int(CHAT_ID), msg)

scheduler.add_job(check_birthdays, "cron", hour=8, minute=30)

@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await message.answer("Бот для поздравлений запущен!")

@dp.message_handler(commands=["get_chat_id"])
async def get_chat_id(message: types.Message):
    global CHAT_ID
    CHAT_ID = message.chat.id
    save_chat_id(CHAT_ID)
    await message.answer(f"✅ CHAT_ID этой группы сохранён: `{CHAT_ID}`", parse_mode="Markdown")

@dp.message_handler(commands=["add_employee"])
async def add_employee(message: types.Message):
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("❌ Формат: /add_employee Имя ДД-ММ\nНапример: /add_employee Мария 28-02")
        return
    name = parts[1]
    birthday = parts[2]
    employees = load_employees()
    employees.append({"name": name, "birthday": birthday})
    save_employees(employees)
    await message.answer(f"✅ Сотрудник {name} с датой {birthday} добавлен!")

@dp.message_handler(commands=["list_employees"])
async def list_employees(message: types.Message):
    employees = load_employees()
    if not employees:
        await message.answer("📂 Список сотрудников пуст.")
        return
    text = "👥 Список сотрудников:\n"
    for emp in employees:
        text += f"- {emp['name']} — {emp['birthday']}\n"
    await message.answer(text)

@dp.message_handler(commands=["remove_employee"])
async def remove_employee(message: types.Message):
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("❌ Формат: /remove_employee Имя\nНапример: /remove_employee Мария")
        return
    name = parts[1]
    employees = load_employees()
    new_employees = [emp for emp in employees if emp["name"].lower() != name.lower()]
    if len(new_employees) == len(employees):
        await message.answer(f"⚠️ Сотрудник {name} не найден.")
        return
    save_employees(new_employees)
    await message.answer(f"🗑 Сотрудник {name} удалён.")

@dp.message_handler(commands=["edit_employee"])
async def edit_employee(message: types.Message):
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("❌ Формат: /edit_employee Имя ДД-ММ\nНапример: /edit_employee Иван 15-07")
        return
    name = parts[1]
    new_birthday = parts[2]
    employees = load_employees()
    found = False
    for emp in employees:
        if emp["name"].lower() == name.lower():
            emp["birthday"] = new_birthday
            found = True
            break
    if not found:
        await message.answer(f"⚠️ Сотрудник {name} не найден.")
        return
    save_employees(employees)
    await message.answer(f"✏️ Дата рождения сотрудника {name} изменена на {new_birthday}.")

async def on_startup(_):
    scheduler.start()

if __name__ == "__main__":
    asyncio.run(dp.start_polling(on_startup=on_startup))
