import json


info = "{'currentTimestep': 20, 'netThrust': 43025911.45, 'currentAcceleration': 5.862798554, 'currentVelocityDelta': 5.862798554, 'currentVelocity': 124.429581, 'currentAltitudeDelta': 124.429581, 'currentAltitude': 1362.486283, 'requiredThrustChange': 65.07381915}"

print(json.loads(info))
