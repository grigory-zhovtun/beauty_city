import asyncio
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Update
from bot import setup_bot

@csrf_exempt
async def webhook(request):
    app = setup_bot()
    async with app:
        update = Update.de_json(json.loads(request.body), app.bot)
        await app.process_update(update)
    return JsonResponse({"status": "ok"})
