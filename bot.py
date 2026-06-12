# Importamos las clases necesarias de la librería python-telegram-bot.
# - Update: representa un mensaje o interacción del usuario.
# - InlineKeyboardButton / InlineKeyboardMarkup: sirven para crear botones.
# - ApplicationBuilder: crea la aplicación del bot.
# - CommandHandler: maneja comandos como /start o /juegos.
# - CallbackQueryHandler: maneja los clics en botones.
# - ContextTypes: contexto que acompaña cada actualización.
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Aquí pones el token que te dio BotFather.
# Es la "contraseña" que permite a tu script controlar tu bot.
TOKEN = "8979222729:AAGyrUENCjLClA2pMrj5l7zGzVLS6rFqemA"


# -----------------------------
#   COMANDO /start
# -----------------------------
# Esta función se ejecuta cuando el usuario escribe /start.
# 'update' contiene la información del mensaje.
# 'context' contiene datos adicionales (no lo usamos aún).
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Enviamos un mensaje simple al usuario.
    await update.message.reply_text("¡Bienvenido! Usa /juegos para ver los minijuegos disponibles.")


# -----------------------------
#   COMANDO /juegos
# -----------------------------
# Muestra el menú principal con los 3 juegos.
async def juegos(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Creamos una lista de botones.
    # Cada botón tiene un texto visible y un "callback_data" que identifica qué botón se pulsó.
    keyboard = [
        [InlineKeyboardButton("Would you rather ❓", callback_data="menu_wyr")],
        [InlineKeyboardButton("Trivial 🧠", callback_data="menu_trivial")],
        [InlineKeyboardButton("Verdad o reto 🔥", callback_data="menu_vr")]
    ]

    # Enviamos el mensaje con los botones debajo.
    await update.message.reply_text(
        "Elige un juego:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# -----------------------------
#   CALLBACK GENERAL
# -----------------------------
# Esta función se ejecuta SIEMPRE que el usuario pulse un botón.
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # 'query' representa el botón que se pulsó.
    query = update.callback_query

    # Telegram requiere que confirmemos que hemos recibido el clic.
    await query.answer()

    # 'data' es el texto oculto que pusimos en callback_data.
    data = query.data


    # ============================================================
    #   SUBMENÚ: WOULD YOU RATHER
    # ============================================================
    if data == "menu_wyr":
        # Creamos los botones de los modos del juego.
        keyboard = [
            [InlineKeyboardButton("Modo total", callback_data="wyr_total")],
            [InlineKeyboardButton("Modo soft", callback_data="wyr_soft")],
            [InlineKeyboardButton("Modo hardcore", callback_data="wyr_hardcore")]
        ]

        # Editamos el mensaje anterior para mostrar el submenú.
        await query.edit_message_text(
            "Elige un modo de *Would you rather*:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return


    # ============================================================
    #   SUBMENÚ: TRIVIAL
    # ============================================================
    if data == "menu_trivial":
        keyboard = [
            [InlineKeyboardButton("Fácil", callback_data="trivial_facil")],
            [InlineKeyboardButton("Difícil", callback_data="trivial_dificil")],
            [InlineKeyboardButton("Imposible", callback_data="trivial_imposible")],
            [InlineKeyboardButton("Total", callback_data="trivial_total")]
        ]

        await query.edit_message_text(
            "Elige un modo de *Trivial*:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return


    # ============================================================
    #   SUBMENÚ: VERDAD O RETO
    # ============================================================
    if data == "menu_vr":
        keyboard = [
            [InlineKeyboardButton("Modo normal", callback_data="vr_normal")],
            [InlineKeyboardButton("Modo hardcore", callback_data="vr_hardcore")]
        ]

        await query.edit_message_text(
            "Elige un modo de *Verdad o reto*:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return


    # ============================================================
    #   ACCIONES (AÚN NO IMPLEMENTADAS)
    # ============================================================
    # Aquí es donde más adelante conectaremos cada modo con su juego real.

    # -------------------------
    # WOULD YOU RATHER
    # -------------------------

    # Si el usuario ha elegido un modo (soft, hardcore, total)
    if data.startswith("wyr_") and not data.startswith("wyr_ans_"):
        from games.would_you_rather import play_wyr
        await play_wyr(update, context, data)
        return

    # Si el usuario ha elegido una respuesta
    if data.startswith("wyr_ans_"):
        from games.would_you_rather import answer_wyr
        answer = data.replace("wyr_ans_", "")
        await answer_wyr(update, context, answer)
        return

    if data.startswith("trivial_"):
        await query.edit_message_text("Aquí irá el Trivial 😄")
        return

    if data.startswith("vr_"):
        await query.edit_message_text("Aquí irá Verdad o Reto 😄")
        return


# -----------------------------
#   FUNCIÓN PRINCIPAL
# -----------------------------
def main():

    # Creamos la aplicación del bot usando el token.
    app = ApplicationBuilder().token(TOKEN).build()

    # Registramos los comandos.
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("juegos", juegos))

    # Registramos el manejador de botones.
    app.add_handler(CallbackQueryHandler(button))

    print("Bot arrancado…")

    # Iniciamos el bot en modo "polling".
    # Esto significa que el bot pregunta a Telegram constantemente si hay mensajes nuevos.
    app.run_polling()


# Si ejecutamos este archivo directamente (no importado), arrancamos el bot.
if __name__ == "__main__":
    main()
