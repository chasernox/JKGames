# ---------------------------------------------------------
#   MÓDULO: Would You Rather (WYR)
# ---------------------------------------------------------
# Funcionalidades:
# - Carga de preguntas bajo demanda (solo cuando se usan)
# - No repetir preguntas dentro de la misma partida
# - Flujo automático: tras responder, aparece otra pregunta
# - Botón "Volver atrás"
# - Modo persistente (soft / hardcore / total)
# - Compatible con python-telegram-bot v20+
# ---------------------------------------------------------

import json
import random
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


# ---------------------------------------------------------
#   CARGA DE JSON BAJO DEMANDA
# ---------------------------------------------------------

def load_json_file(path):
    """Carga un JSON y devuelve una lista. Si está vacío o no existe, devuelve []."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []  # archivo vacío
            return json.loads(content)
    except FileNotFoundError:
        return []  # archivo no existe


def get_question_pool(mode):
    """Devuelve una lista de preguntas según el modo."""
    if mode == "soft":
        return load_json_file("data/wyr_soft.json")
    if mode == "hardcore":
        return load_json_file("data/wyr_hardcore.json")
    if mode == "total":
        soft = load_json_file("data/wyr_soft.json")
        hard = load_json_file("data/wyr_hardcore.json")
        return soft + hard


# ---------------------------------------------------------
#   FUNCIÓN PRINCIPAL: mostrar una pregunta
# ---------------------------------------------------------
async def play_wyr(update, context, mode_code):

    query = update.callback_query
    mode = mode_code.replace("wyr_", "")

    # Si no existe un pool para este chat, lo creamos
    if "wyr_pool" not in context.chat_data:
        context.chat_data["wyr_pool"] = get_question_pool(mode)

    pool = context.chat_data["wyr_pool"]

    # Si el pool está vacío → reiniciamos
    if not pool:
        pool.extend(get_question_pool(mode))

    # Elegimos una pregunta aleatoria
    q = random.choice(pool)
    pool.remove(q)  # No repetir

    question = q["question"]
    opt1, opt2 = q["options"]

    # Guardamos el modo para answer_wyr()
    context.chat_data["wyr_mode"] = mode_code

    # Botones
    keyboard = [
        [InlineKeyboardButton(opt1, callback_data=f"wyr_ans_{opt1}")],
        [InlineKeyboardButton(opt2, callback_data=f"wyr_ans_{opt2}")],
        [InlineKeyboardButton("⬅ Volver atrás", callback_data="menu_wyr")]
    ]

    await query.edit_message_text(
        question,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ---------------------------------------------------------
#   FUNCIÓN: mostrar respuesta + lanzar nueva pregunta
# ---------------------------------------------------------
async def answer_wyr(update, context, answer_text):

    query = update.callback_query

    # Recuperamos el modo actual
    mode_code = context.chat_data.get("wyr_mode", None)

    # Botón para volver atrás
    keyboard = [
        [InlineKeyboardButton("⬅ Volver atrás", callback_data="menu_wyr")]
    ]

    await query.edit_message_text(
        f"Elegiste: **{answer_text}** 👌\n\nPreparando otra pregunta...",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    # Esperamos 1.5 segundos
    await asyncio.sleep(1.5)

    # Lanzamos otra pregunta automáticamente
    await play_wyr(update, context, mode_code)
