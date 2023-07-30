import json
from json.decoder import JSONDecodeError
import os

import asyncio
from bson import json_util
from bson.regex import Regex
from jsonschema import validate, ValidationError
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from motor import motor_asyncio

MONGODB_CONNECTION_STRING = os.environ["REEL_MONGODB_CONNECTION_STRING"]
MONGODB_DATABASE_NAME = os.environ["REEL_MONGODB_DATABASE_NAME"]

client = motor_asyncio.AsyncIOMotorClient(MONGODB_CONNECTION_STRING)
db = client[MONGODB_DATABASE_NAME]

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


with open("json_schemas/filter.json", "r", encoding="utf-8") as filter_schema_file:
    filter_schema = json.loads(filter_schema_file.read())


class Subscription:
    def __init__(self, websocket, filters):
        self.close = False
        self.websocket = websocket
        self.filters = filters
        self.parse_filters()

    def parse_filters(self):
        collections = {
            0: "set_metadata",
            1: "text_note",
            2: "recommended_server"
        }
        pipeline = []

        if "ids" in self.filters:
            pipeline.append({"fullDocument.id": {"$in": [Regex(f"^{f}" for f in self.filters["ids"])]}})
        if "authors" in self.filters:
            pipeline.append({"fullDocument.pubkey": {"$in": [Regex(f"^{f}" for f in self.filters["authors"])]}})
        if "kinds" in self.filters:
            collections = {kind: collections[kind] for kind in self.filters["kinds"]}
        if "#e" in self.filters:
            pipeline.append({"$and": {"fullDocument.tags.0": "e", "fullDocument.tags.1": {"$in": self.filters["#e"]}}})
        if "#p" in self.filters:
            pipeline.append({"$and": {"fullDocument.tags.0": "p", "fullDocument.tags.1": {"$in": self.filters["#p"]}}})
        if "since" in self.filters:
            pipeline.append({"fullDocument.created_at": {"$gt": self.filters["since"]}})
        if "until" in self.filters:
            pipeline.append({"fullDocument.created_at": {"$lt": self.filters["until"]}})

        pipeline = [{"$match": {"$or": pipeline}}]

        if "limit" in self.filters:
            pipeline.append({"$limit": self.filters["limit"]})

        self.collections = collections
        self.pipeline = pipeline

    async def start_all(self):
        asyncio.gather(*[self.start(collection) for collection in self.collections.values()])

    async def start(self, collection):
        async with db[collection].watch() as change_stream:
            async for change in change_stream:
                if self.close:
                    break
                if change["operationType"] == "insert":
                    await self.websocket.send_text(
                        json.dumps(
                            {k: change["fullDocument"][k] for k in change["fullDocument"] if k != "_id"},
                            default=json_util.default
                        )
                    )

    def stop(self):
        self.close = True



@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    subscriptions = {}

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
                    # set_metadata
                    case 0:
                        await db.set_metadata.insert_one({ **event, "content": json.loads(event["content"]) })
                    # text_note
                    case 1:
                        await db.text_note.insert_one(event)
                    # recommended_server
                    case 2:
                        await db.recommended_server.insert_one(event)
            case ["REQ", subscription_id, filters]:
                try:
                    validate(filters, filter_schema)
                except ValidationError as error:
                    await websocket.send_text(f"Invalid filter: {error}")
                    continue

                subscription = Subscription(websocket, filters)
                await subscription.start_all()
                subscriptions[subscription_id] = subscription
                print(subscriptions)
            case ["CLOSE", subscription_id]:
                subscriptions[subscription_id].stop()
                del subscriptions[subscription_id]
        await websocket.send_text(f"Message text was: {data}")


@app.on_event("shutdown")
def shutdown_event():
    client.close()
