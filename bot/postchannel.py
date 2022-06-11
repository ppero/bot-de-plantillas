import os
import logging
import bot.constants as con
from typing import Dict

from telegram import (
    Update,
    ParseMode,
    BotCommand,
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    Updater,
    Filters,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    ConversationHandler,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def facts_to_str(user_data: Dict[str, str]):
    nombre = user_data['nombre']
    partes = user_data['partes']
    tamaño = user_data['tamaño']
    capitulos = user_data['capitulos']
    temporada = user_data['temporada']
    argumento = user_data['argumento']
    resolucion = user_data['resolucion']
    return (
        f'🎴<b>{nombre}🎴</b>\n🎬 <b>Resolución:</b> {resolucion}\n📦 <b>Tamaño:</b> {tamaño}'
        f'\n🎥 <b>Capitulos:</b> {capitulos}\n🗜️ <b>Partes:</b> {partes}\n🎞 <b>Temporada:</b> {temporada}\n'
        f'\n📝 <b>Argumento:</b> {argumento}\n📤'
        '<b>Subido por:</b> <a href="tg://user?id={user}">{name}</a>\n\n'
        'CANAL👇\n🎴 <a href=""><b>☁️CLOUD☁️ □ Descargas.Gratis □</b></a> 🎴'
    )


def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name

    if user_id in con.administradores:
        update.message.reply_text(
            text=f'Hola <a href="tg://user?id={user_id}">{first_name}</a>\nPulsa /comenzar para generar una plantilla.',
            parse_mode=ParseMode.HTML
            )
        context.bot.set_my_commands([
            BotCommand(command='comenzar', description='Generar una plantilla.'),
            BotCommand(command='cancelar', description='Detener el proceso actual.')
            ]
        )
    else:
        update.message.reply_text(
            text=f'<a href="tg://user?id={user_id}">{first_name}</a> no tienes acceso para usar este bot.',
            parse_mode=ParseMode.HTML
            )


def comenzar(update: Update, context: CallbackContext):
    if update.effective_user.id in con.administradores:
        update.message.reply_text(
            "Enviame la imagen de la plantilla.",
            )
        return con.PHOTO


def photo(update: Update, context: CallbackContext):
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('bot/photo/{}.jpg'.format(update.message.chat_id))
    update.message.reply_text(
        'Enviame el nombre del archivo.'
    )
    return con.NOMBRE


def nombre(update: Update, context: CallbackContext):
    text = update.message.text
    context.user_data['nombre'] = text
    update.message.reply_text(
        f'Enviame la calidad del archivo.'
    )
    return con.CALIDAD_VIDEO


def resolution(update: Update, context: CallbackContext):
    text = update.message.text
    context.user_data['resolucion'] = text
    update.message.reply_text(
        f'Enviame el peso del archivo.'
    )
    return con.SIZE


def peso(update: Update, context: CallbackContext):
    text = update.message.text
    context.user_data['tamaño'] = text
    update.message.reply_text(
        f'Enviame el número de capitulos.'
    )
    return con.CAPITULOS


def capitulos(update: Update, context: CallbackContext):
    text = update.message.text
    context.user_data['capitulos'] = text
    update.message.reply_text(
        f'Enviame el número de partes.'
    )
    return con.PARTES


def partes(update: Update, context: CallbackContext):
    text = update.message.text
    context.user_data['partes'] = text
    update.message.reply_text(
        f'Enviame la temporada.'
    )
    return con.TEMPORADA


def temporada(update: Update, context: CallbackContext):
    text = update.message.text
    context.user_data['temporada'] = text
    update.message.reply_text(
        f'Enviame el argumento.'
    )
    return con.ARGUMENTO


def argumento(update: Update, context: CallbackContext):
    text = update.message.text
    context.user_data['argumento'] = text

    user_id = update.effective_user.id
    first_name = update.effective_user.first_name

    update.message.reply_text(
        text=f"✅ Plantilla creada correctamente\n<b>Resultado:</b>\n\n{facts_to_str(context.user_data)}".format(user=user_id, name=first_name) +
            "\n\nPulsa el botón de debajo para enviar la plantilla. 📢",
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup([['Enviar plantilla ✅']],
            one_time_keyboard=True,
            resize_keyboard=True
            )
        )
    return con.SEND


def done(update: Update, context: CallbackContext):
    user_data = context.user_data
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name

    update.message.reply_text(
        text='Plantilla enviada con éxito. ✅',
        reply_markup=ReplyKeyboardRemove(selective=True))

    context.bot.send_photo(
        chat_id=con.CHANNEL,
        photo=open(f'bot/photo/{update.message.chat_id}.jpg', 'rb'),
        caption=f'{facts_to_str(user_data)}'.format(user=user_id, name=first_name),
        parse_mode=ParseMode.HTML,
    )
    user_data.clear()
    return ConversationHandler.END


def stop(update: Update, context: CallbackContext):
    if update.effective_user.id in con.administradores:
        update.message.reply_text(
            text='Operación cancelada.',
            reply_markup=ReplyKeyboardRemove(selective=True)
        )
        return ConversationHandler.END

def main():
    token = os.getenv('TELEGRAM_TOKEN')
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('comenzar', comenzar)],
        states={
            con.PHOTO: [
                MessageHandler(Filters.photo, photo),
            ],
            con.NOMBRE: [
                MessageHandler(Filters.text, nombre)
            ],
            con.CALIDAD_VIDEO: [
                MessageHandler(Filters.text, resolution)
            ],
            con.SIZE: [
                MessageHandler(Filters.text, peso)
            ],
            con.CAPITULOS: [
                MessageHandler(Filters.text, capitulos)
            ],
            con.PARTES: [
                MessageHandler(Filters.text, partes)
            ],
            con.TEMPORADA: [
                MessageHandler(Filters.text, temporada),
            ],
            con.ARGUMENTO: [
                MessageHandler(Filters.text, argumento),
            ],
            con.SEND: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Enviar plantilla ✅$')), done),
            ],
        },
        fallbacks=[
            MessageHandler(Filters.regex('^Enviar plantilla ✅$'), done),
            CommandHandler('cancelar', stop),
            ],
        allow_reentry=True
    )
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
