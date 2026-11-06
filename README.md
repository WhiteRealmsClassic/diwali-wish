# Diwali Wish — Discord External Application

A small Python Discord application. A user runs `/wish` in the app's DM and receives a Diwali embed with an image bundled in this repository.

It uses Discord's HTTP Interactions Endpoint (not a Gateway bot loop), verifies Discord's Ed25519 request signatures, and only accepts the `BOT_DM` interaction context.

## Requirements

- Python 3.10+
- A Discord application in the Developer Portal
- A public HTTPS URL for the interaction endpoint

## Discord Developer Portal setup

1. Create an application at https://discord.com/developers/applications.
2. In **General Information**, copy the **Application ID** and **Public Key**.
3. In **Bot**, add a bot user and reset/copy its token. Keep the token private.
4. In **Installation**, enable **User Install** and add the `applications.commands` scope to its default install settings.
5. After deployment, set the **Interactions Endpoint URL** to `https://YOUR-HOST/interactions`.
6. Discord sends a PING to validate the URL.

The command is registered for `USER_INSTALL` and `BOT_DM` only. It is not enabled in server channels or other private channels.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill `.env` with `DISCORD_APPLICATION_ID`, `DISCORD_PUBLIC_KEY`, and `DISCORD_BOT_TOKEN`. Load them with:

```bash
set -a
source .env
set +a
```

Start the server:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

Register the slash command in a second terminal with the same environment variables:

```bash
python register_command.py
```

## Render deployment

The included `render.yaml` defines a free Python web service. Connect this repository to Render and add the three Discord environment variables in the Render dashboard. Once deployed, copy the service URL and set Discord's Interactions Endpoint URL to `https://YOUR-HOST/interactions`.

## Test

Install the application using its user-install link, open the app's DM, and run `/wish`. The response includes the bundled `assets/diwali.png` image.

## Security notes

- Never commit `.env`, bot tokens, or other secrets to GitHub.
- The image is uploaded with the interaction response; Discord does not need to fetch an external image URL.
- Discord must be able to reach the endpoint over public HTTPS.
