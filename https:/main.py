import asyncio
import logging
import io
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import BufferedInputFile

# --- SOZLAMALAR ---
TELEGRAM_TOKEN = "8756062505:AAHt6DmGFu7kDng2R5jhdnLsZMCVexJGyHw"  # @pixelgenUZbot tokeningiz
HF_TOKEN = "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"  # Siz bergan Hugging Face tokeningiz

# Stable Diffusion API manzili (bepul va ommabop rasm modeli)
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-3.5-large"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"Salom, {message.from_user.first_name}!\n"
        "🎨 Men PixelGen botiman. Menga istalgan matn (prompt) yozing, va men sizga rasm yasab beraman!"
    )

@dp.message(lambda message: message.text and not message.text.startswith('/'))
async def generate_image(message: types.Message):
    prompt = message.text
    wait_msg = await message.answer("⏳ Rasm chizilyapti, ozgina kuting...")

    try:
        async with aiohttp.ClientSession() as session:
            payload = {"inputs": prompt}
            async with session.post(API_URL, headers=HEADERS, json=payload) as response:
                if response.status == 200:
                    image_bytes = await response.read()
                    
                    # Rasmni Telegramga yuborish
                    photo = BufferedInputFile(image_bytes, filename="image.jpg")
                    await bot.delete_message(chat_id=message.chat.id, message_id=wait_msg.message_id)
                    await message.answer_photo(photo=photo, caption=f"✨ Prompt: {prompt}", parse_mode="Markdown")
                else:
                    error_text = await response.text()
                    await bot.edit_message_text(
                        f"❌ Model hozir band yoki yuklanmoqda. Birozdan keyin qayta urinib ko'ring.\n{error_text[:100]}",
                        chat_id=message.chat.id,
                        message_id=wait_msg.message_id
                    )

    except Exception as e:
        await bot.edit_message_text(
            f"❌ Xatolik yuz berdi: {e}",
            chat_id=message.chat.id,
            message_id=wait_msg.message_id
        )

async def main():
    print("Rasm yasash boti ishga tushdi...")
    await dp.start_polling(bot)

if name == "main":
    asyncio.run(main())
