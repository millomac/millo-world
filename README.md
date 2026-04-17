# Meeting Notes Automation

Script que detecta transcripts de Google Meet en Google Drive, genera meeting notes con Claude y las envía a Slack y Notion.

## Cómo funciona

1. Busca en Google Drive archivos que contengan "Domain Refinement" en el nombre
2. Descarga los transcripts que aún no han sido procesados
3. Claude analiza el transcript y extrae: resumen, participantes, decisiones, action items, parking lot y próximos pasos
4. Publica las notas en el canal de Slack configurado
5. Crea una página en la base de datos de Notion

## Setup

### 1. Instalar dependencias

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus credenciales
```

### 3. Obtener credenciales de Google Drive

1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. Crea un proyecto nuevo (o usa uno existente)
3. En "APIs y servicios" → "Biblioteca", busca y habilita **Google Drive API**
4. Ve a "APIs y servicios" → "Credenciales" → "Crear credenciales" → **ID de cliente OAuth 2.0**
5. Tipo de aplicación: **Aplicación de escritorio**
6. Descarga el JSON y guárdalo como `credentials.json` en la raíz del proyecto
7. La primera vez que corras el script, se abrirá el navegador para autorizar el acceso

### 4. Obtener token de Slack

1. Ve a [api.slack.com/apps](https://api.slack.com/apps) → "Create New App"
2. En "OAuth & Permissions" → "Bot Token Scopes" agrega: `chat:write`
3. Instala la app en tu workspace
4. Copia el **Bot User OAuth Token** (`xoxb-...`) al `.env`
5. Invita el bot al canal: `/invite @nombre-del-bot`
6. El `SLACK_CHANNEL_ID` es el ID del canal (click derecho en el canal → "Ver detalles del canal")

### 5. Obtener token de Notion

1. Ve a [notion.so/my-integrations](https://www.notion.so/my-integrations) → "New integration"
2. Copia el **Internal Integration Secret** (`secret_...`) al `.env`
3. En tu base de datos de Notion → "..." → "Add connections" → selecciona tu integración
4. El `NOTION_DATABASE_ID` está en la URL de la base de datos:
   `https://notion.so/workspace/**<DATABASE_ID>**?v=...`

La base de datos debe tener estas propiedades:
- `Name` — tipo **Title**
- `Date` — tipo **Date**

## Uso

```bash
# Correr manualmente
python main.py

# Programar con cron (cada hora)
0 * * * * cd /ruta/al/proyecto && .venv/bin/python main.py >> logs/cron.log 2>&1
```

## Estructura del proyecto

```
.
├── main.py                      # Punto de entrada
├── meeting_notes/
│   ├── config.py                # Configuración desde variables de entorno
│   ├── drive.py                 # Cliente de Google Drive
│   ├── processor.py             # Procesamiento con Claude API
│   ├── slack_notifier.py        # Envío a Slack
│   ├── notion_notifier.py       # Creación de página en Notion
│   └── state_manager.py         # Tracking de transcripts procesados
├── .env.example                 # Plantilla de variables de entorno
├── requirements.txt
└── .gitignore
```

Los archivos `credentials.json`, `token.json`, `state.json` y `.env` están en `.gitignore` — nunca los subas al repositorio.
