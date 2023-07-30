db = db.getSiblingDB("reel")

db.createCollection("set_metadata", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      title: "Event validation",
      required: ["id", "pubkey", "created_at", "kind", "tags", "content", "sig"],
      properties: {
        "_id": {
          description: "the Mongo document ID",
          "bsonType": "objectId"
        },
        id: {
          description: "32-bytes lowercase hex-encoded sha256 of the serialized event data",
          bsonType: "string",
          pattern: "^[0-9a-f]{64}$"
        },
        pubkey: {
          description: "32-bytes lowercase hex-encoded public key of the event creator",
          bsonType: "string",
          pattern: "^[0-9a-f]{64}$"
        },
        created_at: {
          description: "unix timestamp in seconds",
          bsonType: "int",
        },
        tags: {
          description: "tags",
          bsonType: "array",
          items: {
            bsonType: "array",
            items: {
              bsonType: "string"
            }
          }
        },
        sig: {
          description: "64-bytes hex of the signature of the sha256 hash of the serialized event data, which is the same as the \"id\" field",
          bsonType: "string",
          pattern: "[0-9a-f]{128}"
        },
        kind: {
          description: "set_metadata",
          bsonType: "int"
        },
        content: {
          description: "the body of the note",
          bsonType: "object",
          properties: {
            "name": {
              description: "Username",
              bsonType: "string"
            },
            "about": {
              description: "User information",
              bsonType: "string"
            },
            "picture": {
              description: "User avatar URL",
              bsonType: "string"
            },
          }
        }
      },
      additionalProperties: false
    }
  }
});

db.createCollection("text_note", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      title: "Event validation",
      required: ["id", "pubkey", "created_at", "kind", "tags", "content", "sig"],
      properties: {
        "_id": {
          description: "the Mongo document ID",
          "bsonType": "objectId"
        },
        id: {
          description: "32-bytes lowercase hex-encoded sha256 of the serialized event data",
          bsonType: "string",
          pattern: "^[0-9a-f]{64}$"
        },
        pubkey: {
          description: "32-bytes lowercase hex-encoded public key of the event creator",
          bsonType: "string",
          pattern: "^[0-9a-f]{64}$"
        },
        created_at: {
          description: "unix timestamp in seconds",
          bsonType: "int",
        },
        tags: {
          description: "tags",
          bsonType: "array",
          items: {
            bsonType: "array",
            items: {
              bsonType: "string"
            }
          }
        },
        sig: {
          description: "64-bytes hex of the signature of the sha256 hash of the serialized event data, which is the same as the \"id\" field",
          bsonType: "string",
          pattern: "[0-9a-f]{128}"
        },
        kind: {
          description: "text_note",
          bsonType: "int"
        },
        content: {
          description: "the body of the note",
          bsonType: "string",
        },
      },
      additionalProperties: false
    }
  }
});

db.createCollection("recommended_server", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      title: "Event validation",
      required: ["id", "pubkey", "created_at", "kind", "tags", "content", "sig"],
      properties: {
        "_id": {
          description: "the Mongo document ID",
          "bsonType": "objectId"
        },
        id: {
          description: "32-bytes lowercase hex-encoded sha256 of the serialized event data",
          bsonType: "string",
          pattern: "^[0-9a-f]{64}$"
        },
        pubkey: {
          description: "32-bytes lowercase hex-encoded public key of the event creator",
          bsonType: "string",
          pattern: "^[0-9a-f]{64}$"
        },
        created_at: {
          description: "unix timestamp in seconds",
          bsonType: "int",
        },
        tags: {
          description: "tags",
          bsonType: "array",
          items: {
            bsonType: "array",
            items: {
              bsonType: "string"
            }
          }
        },
        sig: {
          description: "64-bytes hex of the signature of the sha256 hash of the serialized event data, which is the same as the \"id\" field",
          bsonType: "string",
          pattern: "[0-9a-f]{128}"
        },
        kind: {
          description: "recommended_server",
          bsonType: "int"
        },
        content: {
          description: "the body of the note",
          bsonType: "string",
        },
      },
      additionalProperties: false
    }
  }
});
