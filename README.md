# XDrive Car Rental API
## Setup Instructions
### Clone the repository
```bash
git clone https://github.com/Macarious-GK/Xride.git
cd Xride

```
### Set up a virtual environment
```bash
python -m venv env
env\Scripts\activate
pip install -r requirements.txt

```
### Run the server
```python
python manage.py migrate
python manage.py runserver

```
### Admin User Creds: Name(admin)/Password(admin)

## End Points
- GET /cars/ — List all cars.
- POST /cars/ — Create a new car.
- GET /cars/{id}/ — Retrieve a specific car.
- PUT /cars/{id}/ — Update a car.
- DELETE /cars/{id}/ — Delete a car.