import re
from bson.objectid import ObjectId
import pymongo


class UsersDataAccess:
    def __init__(self):
        server = pymongo.MongoClient("mongodb://localhost:27017/")
        db = server["my_project"]
        self.users = db['users']

    def get_all_users(self):
        return self.users.find()

    def search_users(self, term):
        if not term:
            usr = self.users.find()
        else:
            usr = self.users.find(
                {'$or': [
                    {
                        'firstName': {
                            "$regex": re.compile(term, re.IGNORECASE)
                        }
                    },
                    {
                        'lastName': {
                            "$regex": re.compile(term, re.IGNORECASE)
                        }
                    }
                ]
                })

        return usr.sort("firstName")

    def insert_user(self, first_name, last_name, phone_number, dob, gender, address, email, password, education_degree):
        return self.users.insert_one({"firstName": first_name,
                                      "lastName": last_name,
                                      "phoneNumber": phone_number,
                                      "dob": dob,
                                      "gender": gender,
                                      "address": address,
                                      "email": email,
                                      "password": password,
                                      "education_degree": education_degree})

    def get_user_by_id(self, _id: str):
        return self.users.find_one({"_id": ObjectId(_id)})

    def update_user(self, _id, first_name, last_name, phone_number, dob, gender, address, email, education_degree):
        self.users.update_one({"_id": ObjectId(_id)}, {"$set": {"firstName": first_name,
                                                                "lastName": last_name,
                                                                "phoneNumber": phone_number,
                                                                "dob": dob,
                                                                "gender": gender,
                                                                "address": address,
                                                                "email": email,
                                                                "education_degree": education_degree}})

    def change_password(self, _id, password: str):
        self.users.update_one({"_id": ObjectId(_id)}, {
                              "$set": {"password": password}})
