import sys
import os
import time
import telnetlib
import paramiko
import openpyxl

USER_LOGIN = "u0_a292"
USER_PASSWORD = None 
IP_COLUMN_NAME = "ip"
PORT_COLUMN_NAME = "port"
PASSWORD_COLUMN_NAME = "password"
SHEET_NAME = "TestTermux"

log_file = None
whatif_mode = True

#
# TODO: Добавить timeout для telnet через сокет или через threding
#

def connect_telnet(ip, port, username, password, new_password):
    try:
        tn = telnetlib.Telnet(ip, port, timeout = 5)
        tn.read_until(b"login: ")
        tn.write(username.encode('utf-8') + b"\n")
        tn.read_until(b"Password: ")
        tn.write(password.encode('utf-8') + b"\n")

        if whatif_mode:
            log_action(f"WHATIF: IP: {ip}:{port} - Пароль будет изменён на: {new_password}")
        else:
            tn.read_until(b"# ")
            tn.write(b"password\n")
            tn.read_until(b"New password: ")
            tn.write(new_password.encode('utf-8') + b"\n")
            tn.read_until(b"Retype new password: ")
            tn.write(new_password.encode('utf-8') + b"\n")

            log_action(f"IP: {ip}:{port} - Пароль изменён на: {new_password}")

        tn.write(b"exit\n")
        tn.read_all()
        return True
    except Exception as e:
        log_error(f"IP: {ip}:{port} PW: {password} - Telnet ошибка подключения - {str(e)}")
        return False


def connect_ssh(ip, port, username, password, new_password):

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, port, username = username, password = password, timeout = 5)

        if whatif_mode:
            log_action(f"WHATIF: {ip}:{port} - Пароль будет изменён на: {new_password}")
        else:
            stdin, stdout, stderr = client.exec_command(f"passwd")
            stdin.write(password + "\n")
            stdin.write(new_password + "\n")
            stdin.write(new_password + "\n")
            stdin.flush()

            log_action(f" {ip}:{port} - Пароль изменён на: {new_password}")

        client.close()
        return True
    except Exception as e:
        log_error(f" {ip}:{port} PW: {password} - SSH ошибка подключения - {str(e)}")
        return False


def log_action(action):
    log(action, False)

def log_error(error):
    log(error, True)
    log_action(error)

def log(msg, error):
    global log_file

    timestamp_filename = time.strftime("%Y-%m-%d")
    timestamp_log = time.strftime("%Y-%m-%d %H:%M:%S")

    # Если ошибка, то запишет лог в дополнительный файл только с ошибками
    if(error): 
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Log")
        log_filename = f"{timestamp_filename}.txt"
    else:
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Error Log")
        log_filename = f"{timestamp_filename} Error.txt"

    os.makedirs(log_dir, exist_ok=True)    
    log_path = os.path.join(log_dir, log_filename)
    
    with open(log_path, 'a', encoding='utf-8') as file:
        file.write(f"[{timestamp_log}] - {msg}\n")


def main():
    global log_file, whatif_mode

    # Чтение аргументов и установка режима WHATIF
    
    args = sys.argv[1:]
    whatif_mode = '-whatif' in args

    if whatif_mode:
        args.remove('-whatif')

    if len(args) < 2:
        print("Usage: passchanger.py [-whatif] excel_file.xlsx passwords.txt")
        return

    excel_file = args[0]
    password_file = args[1]

    # Парсинг эксель файла 
    
    print("Получение данных из excel")
    workbook = openpyxl.load_workbook(excel_file)
    sheet = workbook[SHEET_NAME]
    headers = [cell.value for cell in sheet[1]]
    ip_column_index = headers.index(IP_COLUMN_NAME)
    port_column_index = headers.index(PORT_COLUMN_NAME)
    password_column_index = headers.index(PASSWORD_COLUMN_NAME)
    
    # Итеративная обработка записей с попыткой подключения через Telnet или SSH
    for row in sheet.iter_rows(min_row=2, values_only=True):
        ip = row[ip_column_index]
        port = row[port_column_index]
        password = row[password_column_index]
        
        with open(password_file, 'r') as file:
            new_password = file.readline().strip()
        
        print(F"Cоединения с {ip}:{port} с паролем {password}")
        if not connect_telnet(ip, port, USER_LOGIN, password, new_password):
            connect_ssh(ip, port, USER_LOGIN, password, new_password)


if __name__ == "__main__":
    main()
