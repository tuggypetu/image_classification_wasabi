
# import nest_asyncio
import os
import glob
import logging
from telegram import Update, InputMediaDocument, InputMediaPhoto
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler

from image_recieve_tets import classify_image, upload_to_wasabi, download_from_wasabi, retrieve_metadata

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
    fname = str(file)
    print(fname)
    print("Classifying.............")
    predicted_class = classify_image(fname)
    print(f"Image classified as: {predicted_class}")

    wasabi_url = upload_to_wasabi(fname, fname, predicted_class)


    files = []
    for t in image_file_types:
        files.extend(glob.glob(t))
    for i in files:
      os.remove(i)

    if wasabi_url:
        print(f"Image uploaded to: {wasabi_url}")
        retrieve_metadata(fname)
        
        # download_path = './Downloaded_' + fname  
        # download_from_wasabi(fname, download_path)
        # print("image downloaded to", download_path)

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

        file_names = ["car.jpg", "file_7.jpg"]

        for fname in file_names:
          download_path = 'image_store/' + fname  
          download_from_wasabi(fname, download_path)
          print("image downloaded to", download_path)
        
        await context.bot.send_media_group(chat_id=update.effective_chat.id, media=get_media_list())

        for i in file_names:
          os.remove(i)



# if __name__ == '__main__':
application = ApplicationBuilder().token(access_token).build()

start_handler = CommandHandler('start', start)
application.add_handler(start_handler)

# echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
# application.add_handler(echo_handler)
download_handler = MessageHandler(filters.PHOTO, downloader)
application.add_handler(download_handler)

upload_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), uploader)
application.add_handler(upload_handler)

# Apply nest_asyncio to allow nested event loops
# nest_asyncio.apply() 
application.run_polling()