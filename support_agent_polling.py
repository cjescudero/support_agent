from swarm import Swarm, Agent
from swarm.repl import run_demo_loop
import pandas as pd
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes
import os
from dotenv import load_dotenv
import argparse
from instructions import instructions


def search_customer_by_dni(dni: str) -> dict:
    """
    Busca un cliente en el archivo CSV según su DNI.
    """
    if not dni or not isinstance(dni, str):
        print(f"DNI inválido: {dni}")
        return {"error": "El DNI proporcionado no es válido"}

    dni = dni.strip().upper()
    print(f"Buscando DNI: {dni}")

    try:
        df = pd.read_csv("data/bbdd_clientes.csv")

        if "DNI" not in df.columns:
            return {"error": "El archivo CSV no contiene la columna 'DNI'"}

        df["DNI"] = df["DNI"].astype(str).str.strip().str.upper()

        # print(f"Primeros DNIs en el CSV: {df['DNI'].head().tolist()}")

        cliente = df[df["DNI"] == dni]
        print(f"Coincidencias encontradas: {len(cliente)}")
        # print(cliente)

        if len(cliente) > 0:
            clientes_list = []
            for _, row in cliente.iterrows():
                cliente_dict = row.to_dict()
                clientes_list.append(
                    {k: str(v) if pd.isna(v) else v for k, v in cliente_dict.items()}
                )
            return {"clientes": clientes_list}
        else:
            return {"error": "No se encontró ningún cliente con ese DNI"}

    except FileNotFoundError:
        print("Error: Archivo no encontrado en data/bbdd_clientes.csv")
        return {"error": "No se pudo encontrar el archivo de la base de datos"}
    except pd.errors.EmptyDataError:
        return {"error": "El archivo de la base de datos está vacío"}
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return {"error": f"Error al buscar el cliente: {str(e)}"}


def pretty_print_messages(messages):
    """Imprime los mensajes del chat de manera formateada."""
    for message in messages:
        if message["role"] == "assistant":
            print(f"\033[94mAsistente\033[0m: {message['content']}")
        elif message["role"] == "function":
            print(f"\033[93mFunción\033[0m: {message['content']}")


def transfer_to_customer_agent():
    """Transfer users to the search customer agent."""
    return customer_agent


def transfer_to_receptionist_agent():
    """Transfer users to the search customer agent."""
    return receptionist_agent


receptionist_agent = Agent(
    name="Agent",
    instructions=instructions,
    functions=[transfer_to_customer_agent],
)

customer_agent = Agent(
    name="Customer Agent",
    instructions="You are a agent that can get the customer information for a given DNI that user must provide.",
    functions=[transfer_to_receptionist_agent, search_customer_by_dni],
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /start"""
    await update.message.reply_text(
        "¡Hola! Soy el asistente virtual de la agencia de seguros Diego Lozano. ¿En qué puedo ayudarte?"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja los mensajes entrantes de Telegram"""
    # print("Mensaje recibido:", update.message)  # Debug

    # Obtener el mensaje del usuario
    user_input = update.message.text
    print("Texto del mensaje:", user_input)  # Debug

    # Verificación más estricta del mensaje
    if user_input is None or user_input.strip() == "":
        print("Mensaje vacío detectado")  # Debug
        await update.message.reply_text("Por favor, envía un mensaje de texto.")
        return

    # Inicializar el historial de mensajes en el contexto si no existe
    if "messages" not in context.user_data:
        context.user_data["messages"] = []
        # print("Inicializando nuevo historial de mensajes")  # Debug

    # Agregar el mensaje del usuario al historial
    context.user_data["messages"].append({"role": "user", "content": user_input})
    # print("Historial actual:", context.user_data["messages"])  # Debug

    try:
        client = Swarm()
        agent = receptionist_agent

        response = client.run(
            agent=agent,
            messages=context.user_data["messages"],
            context_variables={},
            stream=False,
            debug=debug_print.enabled,  # Debug de Swarm
        )

        # Agregar las respuestas al historial y enviarlas al usuario
        for message in response.messages:
            if message["role"] in ["assistant", "function"]:
                if message.get("content"):
                    context.user_data["messages"].append(message)
                    await update.message.reply_text(message["content"])

    except Exception as e:
        print(f"Error en el procesamiento del mensaje: {str(e)}")  # Debug
        await update.message.reply_text(
            "Lo siento, hubo un error al procesar tu mensaje."
        )


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja errores"""
    print(f"Update {update} causó el error {context.error}")
    print(f"Error completo:", exc_info=True)  # Esto mostrará el traceback completo


def parse_arguments():
    """Configura y parsea los argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(description="Bot de asistencia para seguros")
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Activa el modo debug para mostrar mensajes de depuración",
    )
    return parser.parse_args()


def debug_print(*args, **kwargs):
    """Función auxiliar para imprimir mensajes de depuración"""
    if debug_print.enabled:
        print(*args, **kwargs)


debug_print.enabled = False


if __name__ == "__main__":
    # Parsear argumentos de línea de comandos
    args = parse_arguments()
    debug_print.enabled = args.debug

    # Cargar token de Telegram desde variables de entorno
    load_dotenv()
    TOKEN = os.getenv("TELEGRAM_TOKEN")

    debug_print("Iniciando bot...")
    app = Application.builder().token(TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", start_command))

    # Mensajes
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Errores
    app.add_error_handler(error)

    # Iniciar el bot
    print("Bot iniciado...")
    app.run_polling(poll_interval=3)
