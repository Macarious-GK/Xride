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

### Authentication
Obtain a JWT Token through this API and the body of user and Password
- POST /token/


## End Points with JWT
- GET /cars/ — List all cars.
- POST /cars/ — Create a new car.
- GET /cars/{id}/ — Retrieve a specific car.
- PUT /cars/{id}/ — Update a car.
- DELETE /cars/{id}/ — Delete a car.

- Authorization: Bearer your_access_token_here
