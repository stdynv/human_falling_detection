from werkzeug.security import generate_password_hash

password_hash = generate_password_hash("mdpehpad91")
print(password_hash)
