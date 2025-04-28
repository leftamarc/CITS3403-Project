from werkzeug.security import generate_password_hash, check_password_hash

#function to hash a password
def hash_password(password):
    return generate_password_hash(password)

#function to check if the given password matches the hashed password
def check_password(hashed_password, password):
    return check_password_hash(hashed_password, password)