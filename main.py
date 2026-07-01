# main.py

name = "Nahom"
age = 16

gmail = "nahomhenok19@gmail.com"
password = "nahi@1012"

print("===================================")
print("     WELCOME TO NAHOM'S SYSTEM")
print("===================================")

print(f"Name : {name}")
print(f"Age  : {age}")
print(f"Gmail: {gmail}")

user_gmail = input("\nEnter Gmail: ")
user_password = input("Enter Password: ")

if user_gmail == gmail and user_password == password:
    print("\nLogin Successful!")
    print(f"Welcome back, {name}!")
else:
    print("\nWrong Gmail or Password!")