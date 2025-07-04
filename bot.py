import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. الإعدادات وقراءة المفاتيح السرية ---
# سيتم قراءة هذه المفاتيح لاحقاً من إعدادات منصة النشر (Render)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# --- 2. إعداد نموذج Gemini الذكي ---
# استخدام النموذج الأقوى لذكاء أعلى
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro-latest') 

# --- 3. تحديد شخصية البوت (هذا هو "دماغ" البوت) ---
SYSTEM_PROMPT = """
أنت مساعد ذكي ومحترف اسمك "نور". مهمتك هي مساعدة المستخدمين في المجموعات الدراسية أو المحادثات الفردية.
تحدث دائماً باللغة العربية الفصحى بأسلوب ودود ومبسّط.
ابدأ إجاباتك بعبارة ترحيبية لطيفة ومناسبة للسياق.
إذا كان السؤال معقداً، قسّم إجابتك إلى نقاط واضحة لتسهيل الفهم.
لا تخترع إجابات أبداً. إذا لم تكن متأكداً أو لا تعرف الإجابة، قل بكل صراحة: "بصراحة، ليس لدي معلومات كافية حول هذا الموضوع حالياً."
كن إيجابياً ومحفزاً في ردودك.
"""

# --- 4. دوال البوت ---
# دالة الأمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = update.message.from_user.first_name
    await update.message.reply_text(f'أهلاً بك يا {user_name}! أنا نور، مساعدك الدراسي. كيف يمكنني أن أساعدك اليوم؟')

# دالة معالجة الرسائل بذكاء
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    bot_username = (await context.bot.get_me()).username
    user_message = update.message.text
    chat_type = update.message.chat.type

    # الشرط: الرد دائماً في المحادثات الخاصة، أو فقط عند الإشارة (المنشن) في المجموعات
    if chat_type == 'private' or (f"@{bot_username}" in user_message):
        
        # تنظيف الرسالة من المنشن في المجموعات
        if chat_type != 'private':
            user_message = user_message.replace(f"@{bot_username}", "").strip()
            # إذا كانت الرسالة مجرد منشن فارغ، يرد البوت بسؤال
            if not user_message:
                await update.message.reply_text("نعم؟ أنا هنا للمساعدة. اذكرني مع سؤالك.")
                return

        thinking_message = await update.message.reply_text('لحظة من فضلك، أقوم بتجهيز الإجابة... ✍️')
        
        # بناء الموجه الكامل (شخصية البوت + سؤال المستخدم)
        full_prompt = f"{SYSTEM_PROMPT}\n\nسؤال المستخدم: {user_message}"
        
        try:
            response = model.generate_content(full_prompt)
            # تعديل الرسالة "أفكر..." بالإجابة النهائية
            await context.bot.edit_message_text(text=response.text, chat_id=update.message.chat_id, message_id=thinking_message.message_id)
        except Exception as e:
            print(f"Error: {e}")
            await context.bot.edit_message_text(text="عذراً، واجهتني مشكلة أثناء معالجة طلبك. الرجاء المحاولة مرة أخرى.", chat_id=update.message.chat_id, message_id=thinking_message.message_id)

# --- 5. الدالة الرئيسية لتشغيل البوت ---
def main() -> None:
    print("البوت الذكي قيد التشغيل...")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()

if __name__ == '__main__':
    main()
