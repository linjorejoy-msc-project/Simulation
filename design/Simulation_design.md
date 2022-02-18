## Simulation Design

### Links

- https://www.grc.nasa.gov/www/k-12/rocket/rockth.html
- https://www.ijeat.org/wp-content/uploads/papers/v4i5/E4105064515.pdf
- http://www.astronautix.com/l/loxlh2.html
- https://space.stackexchange.com/questions/17563/pros-and-cons-of-lh2-lox-vs-other-fuels
- https://www.grc.nasa.gov/www/k-12/rocket/atmosmet.html

### Constants

- SURFACE_AREA
- KERB_WEIGHT
- INIT_FUEL_WEIGHT
- TIME_STEP_DURATION
- NO_OF_TIMESTEPS

### Global Vars

- timestep_data(HashMap)
  - timestep (Key)=>(Values(HashMap))
    - time
    - timestep
    - fuel_available
    - fuel_flow
    - rocket_weight
    - thrust
    - air_drag_force
    - air_density
    - acceleration
    - velocity
    - altitude
    -

### Inputs

- throttle_pos

---

### Iterating_Functions

---

#### **fuelFlow**

- Parameters
  - **throtle_pos**
- Local Vars
  - **completedTimeStep** = 0
- Function
  - Increase **time_step**
  - Record Time (Optional)
  - Assume Linear Reln between **throttle_pos** and **fuel_flow** and update for that timestep
  - Decrease **fuel_available**
  - Decrease **rocket_weight**
  - store this data in **timestep_data**
  - Keep running every **TIME_STEP_DURATION**

#### **thrustCalc**

- Parameters
  - **fuel_flow**
- Local Vars
  - **completedTimeStep** = 0
- Function
  - Assume Linear Reln between **fuel_flow** and **thrust** and update for that timestep
  - Decrease
  - store this data in **timestep_data**
  - Keep running every **TIME_STEP_DURATION**

#### **visualisation**

- Parameters
  - **\_**
- Local Vars
  - **completedTimeStep** = 0
- Function
  - Visualize live data
  - Keep updating every **TIME_STEP_DURATION**

#### **main**

- Run [fuelFlow](#fuelflow)
- Run [thrustCalc](#thrustcalc)
- Run [visualisation](#visualisation)
-
