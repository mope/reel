import json
from json.decoder import JSONDecodeError
import os

from jsonschema import validate, ValidationError
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from motor import motor_asyncio

app = FastAPI()


MONGODB_CONNECTION_STRING = os.environ["MONGODB_CONNECTION_STRING"]
MONGODB_DATABASE_NAME = os.environ["MONGODB_DATABASE_NAME"]

client = motor_asyncio.AsyncIOMotorClient(MONGODB_CONNECTION_STRING)
db = client[MONGODB_DATABASE_NAME]

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

with open("json_schemas/event.json", "r", encoding="utf-8") as event_schema_file:
    event_schema = json.loads(event_schema_file.read())

@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()

        try:
            message = json.loads(data)
        except JSONDecodeError:
            await websocket.send_text("Invalid message: not JSON")
            continue

        match message:
            case ["EVENT", event]:
                try:
                    validate(event, event_schema)
                except ValidationError as error:
                    await websocket.send_text(f"Invalid event: {error}")
                    continue

                match event["kind"]:
                    case 0:
                        await db.set_metadata.insert_one(event)
                    case 1:
                        await db.text_note.insert_one(event)
                    case 2:
                        await db.recommended_server.insert_one(event)
                print(f"Received event {event}")
            case ["REQ", subscription_id, filters]:
                print(f"Received request {subscription_id} with filters {filters}")
            case ["CLOSE", subscription_id]:
                print(f"Received close request for {subscription_id}")
        await websocket.send_text(f"Message text was: {data}")
