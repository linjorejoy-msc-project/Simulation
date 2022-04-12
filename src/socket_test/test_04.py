import json

CONFIG_DATA = {
    "id": "CLIENT_4",
    "name": "aerodynamics",
    "subscribed_topics": ["motion", "field"],
    "published_topics": ["drag", "field_update"],
    "constants_required": [
        "dragCoefficient",
        "rocketFrontalArea",
        "timestepSize",
        "totalTimesteps",
    ],
    "variables_subscribed": [],
}

string = json.dumps(CONFIG_DATA)

print(string)