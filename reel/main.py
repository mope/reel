import json
from json.decoder import JSONDecodeError

from jsonschema import validate, ValidationError
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()




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
            validate(message, event_schema)
        except (ValidationError, JSONDecodeError) as error:
            await websocket.send_text(f"Invalid message: {error}")
            continue
        match message:
            case ["EVENT", event]:
                print(f"Received event {event}")
            case ["REQ", subscription_id, filters]:
                print(f"Received request {subscription_id} with filters {filters}")
            case ["CLOSE", subscription_id]:
                print(f"Received close request for {subscription_id}")
        await websocket.send_text(f"Message text was: {data}")
