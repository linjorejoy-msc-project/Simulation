import DDS
from DDS import Topic

topics = [
    {
        "name": "fuel_flow",
        "regex": "",
        "parameters_present": [
            "currentMassFlowRate",
            "currentOxidiserMass",
            "currentFuelMass",
            "currentRocketTotalMass",
        ],
    },
    {
        "name": "thrust",
        "regex": "",
        "parameters_present": [
            "currentThrust",
        ],
    },
    {
        "name": "drag",
        "regex": "",
        "parameters_present": [
            "drag",
        ],
    },
    {
        "name": "motion",
        "regex": "",
        "parameters_present": [
            "netThrust",
            "currentAcceleration",
            "currentVelocityDelta",
            "currentVelocity",
            "currentAltitudeDelta",
            "currentAltitude",
            "requiredThrustChange",
        ],
    },
    {
        "name": "field",
        "regex": "",
        "parameters_present": [
            "currentTimestep",
            "currentTime",
            "totalTimestepsRun",
            "versions",
        ],
    },
    {
        "name": "atmosphere",
        "regex": "",
        "parameters_present": [
            "pressure",
            "temperature",
            "density",
        ],
    },
    {"name": "field_update", "regex": "", "parameters_present": []},
    {"name": "field_update_realtime", "regex": "", "parameters_present": []},
    {"name": "motion_update_realtime", "regex": "", "parameters_present": []},
    {"name": "fuel_flow_update_realtime", "regex": "", "parameters_present": []},
]


# dds_obj = DDS.DDSDomain(topics=topics, field_participant="field")
# dds_obj.main()


topic = Topic("some-name", parameters_required=["sas", "asas"])
topic.regex_format = "dadasfsdv3rq3"

print(topic.__dict__)
