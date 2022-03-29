import math


# COMBUSTION
CHAMBER_PRESSURE = 2.27 * 10 ^ 6
CHAMBER_TEMPERATURE = 1200
COEFFICIENT_OF_HEATS = 1.4
CHARECTERISTIC_GAS_CONSTANT = 8.314462
SPECIFIC_GAS_CONSTANT = 355

# LOH/LH2 fuel
O2F_RATIO = 6
DENSITY = 0.28 if O2F_RATIO == 6 else 0.33

# GLOBAL VARIABLE
thrust = 0
altitude = 0


def thrustCalc(
    mass_flow_rate: float,
    exit_velocity: float,
    exit_pressure: float,
    ext_pressure: float,
    exit_area: float,
) -> float:
    return mass_flow_rate * exit_velocity + (exit_pressure - ext_pressure) * exit_area


def externalPressureTemperature(altitude: float):
    T = 0
    P = 0
    if altitude < 11000:
        T = 15.04 - 0.0649 * altitude
        P = 101.29 * [(T + 273.1) / 288.08] ^ 5.256
    elif 11000 <= altitude < 25000:
        T = -56.46
        p = 22.65 * math.exp(1.73 - 0.000157 * altitude)
    else:
        T = -131.21 + 0.00299 * altitude
        P = 2.488 * [(T + 273.1) / 216.6] ^ -11.388
    return P, T


def getAirDensityFromAltitude(altitude: float):
    P, T = externalPressureTemperature(altitude)
    return P / [0.2869 * (T + 273.1)]
