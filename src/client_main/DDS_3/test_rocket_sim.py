import math
import time
import json
import matplotlib.pyplot as plt

CONSTANTS = {
    "gravitationalAcceleration": 9.8,
    "coefficientOfDrag": 0.7,
    "initialVelocity": 0,
    "timestepSize": 1,
}

rocket_variables = {
    "currentAcceleration": 0,
    "currentVelocity": 0,
    "currentAltitude": 0,
    "currentMass": 100000,
    "currentMassFlowRate": 100,
}


def acceleration(
    mass_of_rocket,
    rocket_exhaust_speed,
    mass_of_fuel_used_this_timestep,
):
    term_1 = CONSTANTS["gravitationalAcceleration"]
    term_2 = (
        CONSTANTS["coefficientOfDrag"]
        * rocket_variables["currentVelocity"] ** 2
        / mass_of_rocket
    )
    term_3 = (
        rocket_exhaust_speed
        * mass_of_fuel_used_this_timestep
        / (mass_of_rocket * CONSTANTS["timestepSize"])
    )

    return term_1 + term_2 + term_3


def update_motion(acc):
    rocket_variables["currentAcceleration"] = acc
    rocket_variables["currentVelocity"] = (
        rocket_variables["currentVelocity"] + acc * CONSTANTS["timestepSize"]
    )
    rocket_variables["currentAltitude"] = (
        rocket_variables["currentAltitude"]
        + rocket_variables["currentVelocity"] * CONSTANTS["timestepSize"]
    )


if __name__ == "__main__":
    x = []
    y = []
    for i in range(100):
        x.append(i)
        acc = acceleration(
            rocket_variables["currentMass"],
            500,
            rocket_variables["currentMassFlowRate"],
        )
        rocket_variables["currentMass"] -= rocket_variables["currentMassFlowRate"]
        update_motion(acc)
        print(f'currentAltitude={rocket_variables["currentAltitude"]}')
        y.append(rocket_variables["currentAltitude"])

    plt.plot(x, y)
    plt.show()
