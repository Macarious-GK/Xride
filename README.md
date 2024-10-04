# XDrive Car Rental API

### Clone the repository
```bash
git clone https://github.com/Macarious-GK/Xride.git
cd Xride

```
## Setup Instructions
### Set up a virtual environment
```bash
python -m venv env
source env/bin/activate  # For macOS/Linux
env\Scripts\activate  # For Windows
pip install -r requirements.txt


```
### Run the server
```python
python manage.py migrate
python manage.py runserver

```

### Admin User Creds: 
- Name: admin
- Password: admin

## End Points with JWT

### Authentication
Obtain a JWT Token through this API and the body of user and Password
- POST /token/

### APP: ride_V0
- GET V0/cars/ — List all cars.
- POST V0/cars/ — Create a new car.
- GET V0/cars/{id}/ — Retrieve a specific car.
- PUT V0/cars/{id}/ — Update a car.
- DELETE V0/cars/{id}/ — Delete a car.
- Authorization: Bearer your_access_token_here

### APP: ride_V1

- GET V1/cars/nearby-available/ — Get nearest available cars based on the user's latitude and longitude. "Nearest cars in N KM radius"
- POST V1/car/<int:car_id>/reserve/ — Reserve a specific car by its ID.
- POST V1/car/<int:car_id>/release/ — Release a reserved car, making it available again.
- POST V1/car/<int:car_id>/door-status/ — Change the door status of a specific car (open or close).
- Authorization: Bearer your_access_token_here
