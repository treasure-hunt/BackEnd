# BackEnd

## Endpoints

All endpoints require the headers:

```
authorization: "token TOKEN_KEY_HERE"
```

### Move a single direction once
Endpoint: POST `/traverse/<direction>`
Direction must be `n` `e` `s` or `w` (not case sensitive). If you input a different direction or one that is not possible to move in you will simply be told that there is no room in that direction. We halt your request so you do not get a cooldown for inputting an incorrect direction.

Response:

```
{
    "room_id": 6,
    "title": "A misty room",
    "description": "You are standing on grass and surrounded by a dense mist. You can barely make out the exits in any direction.",
    "coordinates": "(60,58)",
    "elevation": 0,
    "terrain": "NORMAL",
    "players": [],
    "items": [],
    "exits": [
        "n",
        "w"
    ],
    "cooldown": 15,
    "errors": [],
    "messages": [
        "You have walked south.",
        "Wise Explorer: -50% CD"
    ]
}
```

### Get all rooms
Endpoint: GET `/rooms`
Returns every single room with the description/title, coordinates, and the resulting room for every exit. Null in an exit means we either haven't explored it, or there is no exit that direction.

Response:

```
[
    {
        "id": 0,
        "title": "A brightly lit room",
        "description": "You are standing in the center of a brightly lit room. You notice a shop to the west and exits to the north, south and east.",
        "coords": {
            "x": 60,
            "y": 60
        },
        "exits": {
            "n": 10,
            "w": 1,
            "e": 4,
            "s": 2
        },
        "elevation": 0,
        "terrain": "NORMAL"
    },
    {
        "id": 2,
        "title": "A misty room",
        "description": "You are standing on grass and surrounded by a dense mist. You can barely make out the exits in any direction.",
        "coords": {
            "x": 60,
            "y": 59
        },
        "exits": {
            "n": 0,
            "w": null,
            "e": null,
            "s": 6
        },
        "elevation": 0,
        "terrain": "NORMAL"
    }
]
```

### Get single room
Endpoint: GET `/room/<id or name>`
Returns the room based on the provided id or name.

Response:

```
{
    "id": 1,
    "title": "Shop",
    "description": "You are standing in a small shop. A sign behind the mechanical shopkeeper says 'WILL PAY FOR TREASURE'.",
    "coords": {
        "x": 59,
        "y": 60
    },
    "exits": {
        "n": null,
        "w": null,
        "e": 0,
        "s": null
    },
    "elevation": null,
    "terrain": null
}
```

### Start Auto Traversing
Endpoint: POST `/autotraverse`
Your character will start exploring maps that we do not have in our database.

Response:

```
{
    "Message": "Auto Traverse has started."
}
```

### Stop Auto Traversing
Endpoint: DELETE `/autotraverse`
Your character will stop auto traversing the unexplored rooms in our database. Gives up control and stops using your Token.

Response:

```
{
    "Message": "Auto Traverse has been stopped."
}
```