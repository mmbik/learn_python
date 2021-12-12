import re
from typing import Collection
import flask
import pymongo
from jinja2 import Environment, FileSystemLoader
from datetime import date
from users_data_access import UsersDataAccess

sharedParams = {"copyright": date.today().year}
app = flask.Flask(
    __name__,
    template_folder="templates",
    static_folder="assets",
)
app.config["DEBUG"] = True


@app.route("/", methods=['GET'])
def homePage():
    return flask.render_template('home.html', **sharedParams, pageTitle="My Website")


@ app.route("/sign-up", methods=['GET'])
def signUp():
    formData = {'first_name': '', 'last_name': '', 'phone_number': '',
                'dob': '', 'gender': '', 'address': '', 'education_degree': '', 'email': ''}

    return flask.render_template('signup.html', **sharedParams, pageTitle="Register", formData=formData)


@ app.route('/sign-up', methods=['POST'])
def home():
    first_name = flask.request.form["firstName"]
    last_name = flask.request.form["lastName"]
    phone_number = flask.request.form["phoneNumber"]
    dob = flask.request.form["dob"]
    gender = flask.request.form["gender"]
    address = flask.request.form["address"]
    education_degree = flask.request.form["educationDegree"]
    email = flask.request.form["email"]
    password = flask.request.form["password"]
    c_password = flask.request.form["cPassword"]

    formData = {'firstName': first_name, 'lastName': last_name, 'phoneNumber': phone_number,
                'dob': dob, 'gender': gender, 'address': address, 'educationDegree': education_degree, 'email': email}

    errorMessage = ''
    if password != c_password:
        errorMessage = "Password is not matched"

    if not first_name:
        errorMessage = "first name is required"
    if not last_name:
        errorMessage = "last name is required"
    if not email:
        errorMessage = "email is required"
    else:
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not(re.fullmatch(regex, email)):
            errorMessage = "Invalid Email"

    if errorMessage:
        return flask.render_template('signup.html', **sharedParams, pageTitle="Register", message=errorMessage, formData=formData)

    dataAccess = UsersDataAccess()
    dataAccess.insert_user(first_name, last_name, phone_number,
                           dob, gender,  address, email, password, education_degree)
    return flask.render_template('signup.html', **sharedParams, pageTitle="Register", message="Your account has been registered", formData=formData)


@app.route('/users', defaults={'result': None}, methods=['GET'])
@app.route('/users/<result>', methods=['GET'])
def usr(result: str):

    message = ""

    if result == "password-success":
        message = "Password has been changed."

    term = flask.request.args.get("term")
    dataAccess = UsersDataAccess()
    return flask.render_template('users.html', **sharedParams, pageTitle="users", usersList=dataAccess.search_users(term), message=message)


@app.route('/edit-user/<_id>', methods=['GET'])
def editUserGet(_id):
    dataAccess = UsersDataAccess()
    user = dataAccess.get_user_by_id(_id)
    return flask.render_template('edit-user.html', **sharedParams, pageTitle="edit", formData=user)


@app.route('/edit-user/<_id>', methods=['POST'])
def editUserPost(_id):
    dataAccess = UsersDataAccess()

    first_name = flask.request.form["firstName"]
    last_name = flask.request.form["lastName"]
    phone_number = flask.request.form["phoneNumber"]
    dob = flask.request.form["dob"]
    gender = flask.request.form["gender"]
    address = flask.request.form["address"]
    education_degree = flask.request.form["educationDegree"]
    email = flask.request.form["email"]

    dataAccess.update_user(
        _id, first_name, last_name, phone_number, dob, gender, address, email, education_degree)
    return flask.redirect("/edit-user/" + _id)


@app.route('/edit-password/<_id>', methods=['GET'])
def changePasswordGet(_id):
    dataAccess = UsersDataAccess()
    user = dataAccess.get_user_by_id(_id)
    return flask.render_template('edit-password.html', **sharedParams, pageTitle="edit password", formData=user)


@app.route('/edit-password/<_id>', methods=['POST'])
def changePasswordPost(_id):
    dataAccess = UsersDataAccess()
    user = dataAccess.get_user_by_id(_id)
    password = flask.request.form["password"]
    cPassword = flask.request.form["cPassword"]

    passMessage = 'password changed'
    if password != cPassword:
        passMessage = 'password is not match'
        return flask.render_template('edit-password.html', **sharedParams, pageTitle="edit password", message=passMessage, formData=user)
    dataAccess.change_password(_id, password)
    return flask.redirect("/users/password-success")
    # return flask.render_template('edit-password.html', **sharedParams, pageTitle="edit password", message=passMessage, formData=user)


@ app.errorhandler(404)
def not_found(error):
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)
    homeContent = env.get_template('404.html')
    return homeContent.render(pageTitle="Not Found", copyright=date.today().year)


app.run(debug=True)
