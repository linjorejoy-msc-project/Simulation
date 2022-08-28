start cmd.exe /k ".\socket_venv\Scripts\activate.bat & python src\client_2.5_fields.py"
TIMEOUT 3
start cmd.exe /k ".\socket_venv\Scripts\activate.bat & python src\client_2.1_fuel_tank.py"
TIMEOUT 3
start cmd.exe /k ".\socket_venv\Scripts\activate.bat & python src\client_2.2_engine.py"
TIMEOUT 3
start cmd.exe /k ".\socket_venv\Scripts\activate.bat & python src\client_2.3_motion.py"
TIMEOUT 3
start cmd.exe /k ".\socket_venv\Scripts\activate.bat & python src\client_2.6_atmosphere.py"
TIMEOUT 3
start cmd.exe /k ".\socket_venv\Scripts\activate.bat & python src\client_2.8_real_time_updater.py"
TIMEOUT 3