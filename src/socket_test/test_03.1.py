# Imports
import math


# Simulation Constants
"""
`simulationType` 
    1: Based on Number of Timesteps
    2: Based on target Altitude

"""
simulationType = 1
totalTimesteps = 500
currentTimestep = 0
timestepSize = 1
targetAltitude = 50_000

# Rocket Constants
"""

"""
requiredThrust = 123_191_000.0
# currentThrust = requiredThrust
dragCoefficient = 0.75

rocketTotalMass = 7_982_000
rocketUnfuelledMass = 431_000
initialRocketOFMass = rocketTotalMass - rocketUnfuelledMass
O2FRatio = 6
initialOxidiserMass = O2FRatio * initialRocketOFMass / (O2FRatio + 1)
initialFuelMass = initialRocketOFMass / (O2FRatio + 1)
# currentOxidiserMass = initialOxidiserMass
# currentFuelMass = initialFuelMass
# currentRocketTotalMass = rocketTotalMass


rocketBodyDiameter = 21.3
rocketFrontalArea = math.pi * rocketBodyDiameter * rocketBodyDiameter

specificImpulse = 410
gravitationalAcceleration = 9.81
initialRequiredMassFlowRate = requiredThrust / (
    specificImpulse * gravitationalAcceleration
)
# currentMassFlowRate = initialRequiredMassFlowRate

# currentAcceleration = 0
# currentVelocity = 0
# currentVelocityDelta = 0
# currentAltitude = 0
# currentAltitudeDelta = 0

"""
Simulation Helpers
"""


def simulation_complete() -> bool:
    if currentTimestep > totalTimesteps:
        return True
    return False


def external_pressure_temperature(altitude: float):
    T = 0.0
    P = 0.0
    if altitude < 11000:
        T = 15.04 - 0.00649 * altitude
        P = 101.29 * ((T + 273.1) / 288.08) ** 5.256
    elif 11000 <= altitude < 25000:
        T = -56.46
        p = 22.65 * math.exp(1.73 - 0.000157 * altitude)
    else:
        T = -131.21 + 0.00299 * altitude
        P = 2.488 * ((T + 273.1) / 216.6) ** -11.388
    return P, T


def get_air_density(altitude: float):
    P, T = external_pressure_temperature(altitude)
    return P / (0.2869 * (T + 273.1))


"""
Simulation Functions
"""


def fuel_tank(
    thrust,
    currentOxidiserMass,
    currentFuelMass,
    currentRocketTotalMass,
    thrustChangePercent=0,
):
    global specificImpulse
    global gravitationalAcceleration

    # currentThrust = (100 + thrustChangePercent) * currentThrust / 100
    currentMassFlowRate = thrust / (specificImpulse * gravitationalAcceleration)

    massReduced = currentMassFlowRate * timestepSize
    currentOxidiserMass = currentOxidiserMass - (
        massReduced * O2FRatio / (O2FRatio + 1)
    )
    currentFuelMass = currentFuelMass - (massReduced / (O2FRatio + 1))
    if currentFuelMass < 0:
        return 0

    currentRocketTotalMass = currentRocketTotalMass - massReduced

    return (
        currentMassFlowRate,
        currentOxidiserMass,
        currentFuelMass,
        currentRocketTotalMass,
    )


def engine(fuelFlow=initialRequiredMassFlowRate):
    global specificImpulse

    currentThrust = specificImpulse * fuelFlow * gravitationalAcceleration
    # requiredThrustChange = (requiredThrust - currentThrust) * 100 / requiredThrust

    return currentThrust


def aerodynamics(velo, alti):
    global dragCoefficient

    drag = dragCoefficient * get_air_density(alti) * velo * velo * rocketFrontalArea / 2

    return drag


def motion(
    drag, engineThrust, currentVelocity, currentAltitude, currentRocketTotalMass
):
    global gravitationalAcceleration
    global requiredThrust  # is a constant

    netThrust = engineThrust - currentRocketTotalMass * gravitationalAcceleration - drag
    requiredThrustChange = (requiredThrust - netThrust) * 100 / requiredThrust

    currentAcceleration = netThrust / currentRocketTotalMass
    currentVelocityDelta = currentAcceleration * timestepSize
    currentVelocity = currentVelocity + currentVelocityDelta
    currentAltitudeDelta = currentVelocity * timestepSize
    currentAltitude = currentAltitude + currentAltitudeDelta

    return (
        currentAcceleration,
        currentVelocity,
        currentVelocityDelta,
        currentAltitude,
        currentAltitudeDelta,
        requiredThrustChange,
    )


def main():
    global requiredThrust
    global currentTimestep

    currentThrust = requiredThrust  #
    currentOxidiserMass = initialOxidiserMass  #
    currentFuelMass = initialFuelMass  #
    currentRocketTotalMass = rocketTotalMass  #
    thrustChangePercent = 0  #
    currentDrag = 0  #
    currentVelocity = 0  #
    currentAltitude = 0  #

    while not simulation_complete():
        fuel_tank_output = fuel_tank(
            thrust=currentThrust,
            currentOxidiserMass=currentOxidiserMass,
            currentFuelMass=currentFuelMass,
            currentRocketTotalMass=currentRocketTotalMass,
            thrustChangePercent=thrustChangePercent,
        )
        if fuel_tank_output == 0:
            print("Fuel Over")
            break
        (
            currentMassFlowRate,
            currentOxidiserMass,
            currentFuelMass,
            currentRocketTotalMass,
        ) = fuel_tank_output

        currentThrust = engine(fuelFlow=currentMassFlowRate)
        (
            currentAcceleration,
            currentVelocity,
            currentVelocityDelta,
            currentAltitude,
            currentAltitudeDelta,
            requiredThrustChange,
        ) = motion(
            drag=currentDrag,
            engineThrust=currentThrust,
            currentVelocity=currentVelocity,
            currentAltitude=currentAltitude,
            currentRocketTotalMass=currentRocketTotalMass,
        )

        currentDrag = aerodynamics(currentVelocity, currentAltitude)

        print(
            f"Timestep: {currentTimestep:>4} Altitude:{currentAltitude:<20} Velocity: {currentVelocity:<20}"
        )
        currentTimestep = currentTimestep + 1


if __name__ == "__main__":
    main()
