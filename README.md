# Agente de Soporte para Correduría de Seguros

Este proyecto implementa un sistema de agentes conversacionales para una correduría de seguros, permitiendo la búsqueda de información de clientes mediante DNI y la gestión de consultas generales a través de Telegram.

## Características

- Sistema de agentes múltiples con diferentes roles
- Búsqueda de clientes por DNI en base de datos CSV
- Bot de Telegram integrado
- Capacidad de transferencia entre agentes según el tipo de consulta
- Formateo de respuestas para mejor legibilidad
- Manejo de historial de conversaciones
- Sistema de manejo de errores robusto

## Requisitos

- Python 3.7+
- Dependencias:
  - swarm
  - pandas
  - python-telegram-bot
  - python-dotenv
  - requests

## Configuración

1. Clona el repositorio
2. Crea un archivo `.env` en la raíz del proyecto
3. Añade tu token de Telegram al archivo `.env`:
   ```
   TELEGRAM_TOKEN=tu_token_aquí
   ```

## Estructura de Datos

El sistema espera un archivo CSV en `data/bbdd_clientes.csv` con al menos una columna 'DNI' para la búsqueda de clientes.

## Uso

1. Configura las variables de entorno
2. Ejecuta el bot:
   ```bash
   python support_agent.py
   ```
3. Interactúa con el bot a través de Telegram
   - Usa /start para iniciar una conversación
   - Realiza consultas generales o búsquedas por DNI

## Funcionalidades del Bot

- Comando /start para iniciar la interacción
- Búsqueda automática de clientes por DNI
- Respuestas contextuales según el tipo de consulta
- Manejo de conversaciones persistentes