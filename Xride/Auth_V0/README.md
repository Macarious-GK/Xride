# Frontend APIs

- /users/
- /users/me/
- /users/resend_activation/
- /users/set_password/
- /users/reset_password/
- /users/reset_password_confirm/

# Backend APIs

- /auth/activate/<str:uid>/<str:token>/

- /users/activation/
data = {
    'uid': uid,
    'token': token
        }

- /auth/password/reset/confirm/<str:uid>/<str:token>/

- /users/reset_password_confirm/
data = {
    "uid": "",
    "token": "",
    "new_password": "",
    "re_new_password": ""
}

# APIS

## API to create user 
POST /users/
{
    "username": "",
    "email": "",
    "first_name": "",
    "last_name": "",
    "phone_number": "",
    "address": "",
    "national_id": "",
    "password": "",
    "re_password": "",
}

- Then an activation link will be sent to the user's email, after clicking on it the user account is activated
- The server send link activation email and success activation email

## API to Retrive user 
POST-PUT-DELETE /users/me/

Header ["Authorization": "JWT Token"]
- Use this endpoint to retrieve/update
- Used to delete User, require current_password in the DELETE request

## API to resend_activation Email
POST /users/resend_activation/

{
    "email": "",
}

- This resend activation email if the user in not active and the email is in use.
- The server send link activation email and success activation email
- Return Bad Request if the user is Active or the email is not registered

## API to activate user 
GET /auth/activate/<str:uid>/<str:token>/
POST /users/activation/

- These apis are for server use to get the uid and token to activate the user, frist api is sent to the user and by clicking the backend make a POST request api "/users/activation/" with data contain uid & token

## API to Set Password
POST /users/set_password/
Header ["Authorization": "JWT Token"]
body:
{
    "new_password":"",
    "re_new_password":"",
    "current_password":""
}
- Use this endpoint to change user password

## API to Reset Password (NEED WORK WITH FRONTEND)
POST /users/reset_password/
body:
{
    "email":"",
}
GET or POST /auth/password/reset/confirm/<str:uid>/<str:token>/ "UNDER WORK"
POST /users/reset_password_confirm/

- the first API take email and send a link to user email to reset the password.
- Then user use the second API "GET Request" this used by frontend to send a POST request to the thired API with this data:

data = {
    "uid": "",
    "token": "",
    "new_password": "",
    "re_new_password": ""
}


## API JWT Token Authentication
- /jwt/create/
body:
{
    "username": "",
    "password": ""
}
- /jwt/refresh/
body:
{
    "refresh": "refresh_Token",
}
- /jwt/verify/
body:
{
	"token": ""
}



## -------------
DELETE user/delete-photo/
photo_type["personal_photo", "national_id_photo", "licence_photo"]
body:{
    "photo_type": "licence_photo"
}

POST user/upload-photo/
body:{
    "personal_photo": "File",
    "national_id_photo": "File",
    "licence_photo": "File"

}