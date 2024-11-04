from swarm import Swarm, Agent
from swarm.repl import run_demo_loop
import requests
import sys
import pandas as pd


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
    instructions="You are a helpful agent of a insurance borker agency. Answer the user's question in the same language as the question.",
    functions=[transfer_to_customer_agent],
)

customer_agent = Agent(
    name="Customer Agent",
    instructions="You are a agent that can get the customer information for a given DNI that user must provide.",
    functions=[transfer_to_receptionist_agent, search_customer_by_dni],
)

if __name__ == "__main__":
    # run_demo_loop(receptionist_agent)

    stream = False
    debug = False
    context_variables = {}

    client = Swarm()
    print("Starting Swarm CLI")

    messages = []
    agent = receptionist_agent

    while True:
        user_input = input("\033[90mUser\033[0m: ")
        messages.append({"role": "user", "content": user_input})

        response = client.run(
            agent=agent,
            messages=messages,
            context_variables=context_variables,
            stream=stream,
            debug=debug,
        )

        if stream:
            response = process_and_print_streaming_response(response)
        else:
            pretty_print_messages(response.messages)

        messages.extend(response.messages)
        agent = response.agent
