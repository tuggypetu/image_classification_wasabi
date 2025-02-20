
import glob
import logging
from telegram import Update, InputMediaDocument, InputMediaPhoto
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler

# from image_recieve_tets import predicted_class

access_token = ""
image_file_types = ('*.jpg', '*png', '*.jpeg')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

# async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


async def downloader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_file = await update.message.effective_attachment[-1].get_file()
    print(new_file)
    file = await new_file.download_to_drive()
    return file


def get_media_list():
    files = []
    for t in image_file_types:
        files.extend(glob.glob(f"image_store/{t}"))
    media = []
    for f in files:
        # media.append(InputMediaDocument(media=open(f, 'rb')))
        media.append(InputMediaPhoto(media=open(f, 'rb')))
    return media


async def uploader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'send' in update.message.text.lower():
        await context.bot.send_message(chat_id=update.effective_chat.id, text='sending images')
        await context.bot.send_media_group(chat_id=update.effective_chat.id, media=get_media_list())


if __name__ == '__main__':
    application = ApplicationBuilder().token(access_token).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    # echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    # application.add_handler(echo_handler)
    download_handler = MessageHandler(filters.PHOTO, downloader)
    application.add_handler(download_handler)

    upload_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), uploader)
    application.add_handler(upload_handler)

    application.run_polling()