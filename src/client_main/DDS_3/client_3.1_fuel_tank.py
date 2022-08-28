from src.objects.DDS import Participant


config = {
    "id": "CLIENT_1",
    "name": "fuel_flow",
    "subscribed_topics": ["thrust", "field"],
    "non_essential_subscribed_topics": ["fuel_flow_update_realtime"],
    "published_topics": ["fuel_flow"],
    "constants_required": [
        "specificImpulse",
        "gravitationalAcceleration",
        "O2FRatio",
        "initialOxidiserMass",
        "initialFuelMass",
        "rocketTotalMass",
        "timestepSize",
        "totalTimesteps",
    ],
    "variables_subscribed": [],
}


fuel_participant = Participant(CONFIG_DATA=config)
