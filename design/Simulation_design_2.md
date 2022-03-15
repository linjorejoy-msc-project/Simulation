## Simulation Design

---

### Constants

<u>Simulation Constants</u>

- Type:
  - Based on total Time steps or
  - Until Rocket reaches a particlar altitude
- Total Timesteps=100
- Timestep size=1s

http://www.astronautix.com/o/ooststage.html

| Name           | Value      | Unit |
| -------------- | ---------- | ---- |
| Thrust         | 123,191.00 | kN   |
| Gross Mass     | 7,982,000  | kg   |
| Unfuelled Mass | 431,000    | kg   |
| O&F Mass       | 7,551,000  | kg   |
| Sp. Impulse    | 345-410    | s    |
| Diameter       | 21.3       | m    |
| Frontal Area   | 1425.309   | m^2  |

#### **Features**

- Single stage to orbit
- LH2/LOX fuel-oxidizer
  - O2F ratio=6
  - O2F Density=0.28g/cc
  - Sp. Impulse
    - Specific impulse: 451 s
    - Specific impulse sea level: 391 s
    - Location: 2435
    - Isp Shifting: 391 sec
    - Isp Frozen: 388 sec
  - Temperature of Combustion: 2,985 deg K
  - Ratio of Specific Heats: 1.26
  - Characteristic velocity c: 2,435 m/s (7,988 ft/sec)
  - Mol: 10.00 M (32.00 ft)
  - Oxidizer Density: 1.140 g/cc
  - Oxidizer Freezing Point: -219 deg C
  - Oxidizer Boiling Point: -183 deg C
  - Fuel Density: 0.071 g/cc
  - Fuel Freezing Point: -259 deg C
  - Fuel Boiling Point: -253 deg C

---

### DDS Domain

---

### Simulations

1. Aerodynamics
2. Engine and Thrust
3. Fuel Injection
4. Full Simulation

---

1. ### **Aerodynamics**

   - Input
     - Velocity
     - Altitude
   - Output
     - Drag
   - Required Constants of Variables
     - _Air Density_
     - Coeff. of Viscocity
     - Frontal Area
   - Function
     - Consider the Frontal area as a constant and find the Drag force every timestep using the velocity at that time step
     - The density will vary depending on the altitude

2. ### **Engine and Thrust**

   - Input
     - Fuel Flow
   - Output
     - Thrust
     - Change in thrust Percentage
   - Required Constants of Variables
     - _Sp. Impulse_ (need to check which Sp. Impulse to take)
   - Function
     - Using F=Isp\*m_dot\*g_0 we can find thrust(F) at each timestep
     - Sp. Impulse may vary depending on altitude
     - Compare with the required thrust and find the percent of thrust to be changed (+/-)

3. ### **Fuel Injection**

   - Input
     - Change in thrust Percentage
   - Output
     - Fuel Flow
   - Required Constants of Variables
     - Required thrust
   - Function
     - Take the Oxidiser to Fuel Ratio
     - With required thrust,
     - Reduce the weight of the Oxidiser and Fuel with O2F ratio

4. ### **Full Simulation**
   - Input
     - Drag
     - Thrust
   - Output
     - Acceleration
     - Velocity
     - delta_velocity
     - Altitude
     - delta_Altitude
   - Function
     - Find net thrust from resultant of Thrust of Rocket Impulse, Aerodynamic drag and Gravitational Pull due to Load(Which is decreasing) at each timestep
     - Find the Acceleration at that time step with the weight at that timestep
     - Find delta_velocity, current_velocity, delta_altitude, current altitude and send it back
