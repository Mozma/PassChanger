import sys
import os
import telnetlib
import paramiko
import openpyxl
import logging
import datetime

USER_LOGIN = "u0_a292"
USER_PASSWORD = None
TIMEOUT = 3

IP_COLUMN_NAME = "ip"
PORT_COLUMN_NAME = "port"
PASSWORD_COLUMN_NAME = "password"
SHEET_NAME = "TestTermux"

WHATIF_MODE = None

def get_logger(name: str, log_file: str, level: int = logging.INFO):
    """Создаёт новый логер для записи в разные файлы в зависимости от уровня сообщения"""
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

logInfo = get_logger("info", "info.log", logging.INFO)
logError = get_logger("error", "error.log", logging.ERROR)

def connect_telnet(ip, port, username, password, new_password) -> bool:
    """Подключение Telnet для смены пароля"""
    try:
        tn = telnetlib.Telnet(ip, port, timeout=TIMEOUT)
        tn.read_until(b"login: ", timeout=TIMEOUT)
        tn.write(username.encode("utf-8") + b"\n")
        tn.read_until(b"Password: ")
        tn.write(password.encode("utf-8") + b"\n")

        if WHATIF_MODE:
            logInfo.info(f"WHATIF: {ip} - Пароль будет изменён на: {new_password}")
        else:
            tn.read_until(b"# ", timeout=TIMEOUT)
            tn.write(b"password\n")
            tn.read_until(b"New password: ")
            tn.write(new_password.encode("utf-8") + b"\n")
            tn.read_until(b"Retype new password: ")
            tn.write(new_password.encode("utf-8") + b"\n")

            logInfo.info(f"{ip} - Пароль изменён на: {new_password}")

        tn.write(b"exit\n")
        tn.read_all()
        tn.close()
        return True
    except Exception as e:
        logError.error(f"{ip}:{port} Telnet: Не удалось подключиться к устройству - {str(e)}")
        return False

def connect_ssh(ip, port, username, password, new_password) -> bool:
    """Подключение SSH для смены пароля"""
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, port, username=username, password=password, timeout=TIMEOUT)

        if WHATIF_MODE:
            logInfo.info(f"WHATIF: {ip} - Пароль будет изменён на: {new_password}")
        else:
            stdin, stdout, stderr = client.exec_command(f"passwd")
            stdin.write(password + "\n")
            stdin.write(new_password + "\n")
            stdin.write(new_password + "\n")
            stdin.flush()

            logInfo.info(f"{ip} - Пароль изменён на: {new_password}")

        client.close()
        return True
    except Exception as e:
        logError.error(f"{ip}:{port} SSH: Не удалось подключиться к устройству - {str(e)}")
        return False

def create_results_file(results) -> None:
    """Записывает полученные результаты в xlsx файл"""
    output_file = "result.xlsx"
    sheet_name = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")

    # Если файл уже существует, загрузить его
    if os.path.exists(output_file):
        workbook = openpyxl.load_workbook(output_file)
    else:
        workbook = openpyxl.Workbook()

    worksheet = workbook.create_sheet(title=sheet_name)

    # Запись заголовков только если создан новый лист
    if sheet_name == workbook.sheetnames[-1]:
        headers = ["ip", "old_password", "new_password", "changed"]
        for col_num, header in enumerate(headers, 1):
            column_letter = openpyxl.utils.get_column_letter(col_num) # type: ignore
            worksheet[column_letter + "1"] = header

    # Запись данных
    for row_num, result in enumerate(results, start=2):
        worksheet["A" + str(row_num)] = result["ip"]
        worksheet["B" + str(row_num)] = result["old_password"]
        worksheet["C" + str(row_num)] = result["new_password"]
        worksheet["D" + str(row_num)] = result["changed"]

    workbook.save(output_file)
    logInfo.info(f"Результаты сохранены в файле: {output_file}")

def main() -> None:
    """Главный метод"""
    global WHATIF_MODE

    # Чтение аргументов и установка режима WHATIF
    logInfo.info("Скрипт запущен")
    args = sys.argv[1:]
    WHATIF_MODE = "-whatif" in args

    if WHATIF_MODE:
        args.remove("-whatif")

    if len(args) < 2:
        print("Usage: passchanger.py [-whatif] excel_file.xlsx passwords.txt")
        return

    excel_file = args[0]
    password_file = args[1]

    # Парсинг эксель файла
    logInfo.info(f"Получение данных из файла: {excel_file}")
    workbook = openpyxl.load_workbook(excel_file)
    sheet = workbook[SHEET_NAME]
    headers = [cell.value for cell in sheet[1]]
    ip_column_index = headers.index(IP_COLUMN_NAME)
    port_column_index = headers.index(PORT_COLUMN_NAME)
    password_column_index = headers.index(PASSWORD_COLUMN_NAME)

    results = []

    # Итеративная обработка записей с попыткой подключения через Telnet или SSH
    for index, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=1):
        ip = row[ip_column_index]
        port = row[port_column_index]
        password = row[password_column_index]

        with open(password_file, "r", encoding="UTF-8") as file:
            new_password = file.readline().strip()

        print(f"{index}/{sheet.max_row-1} Подключение к устройству {ip}:{port}")
        password_changed = (
            connect_telnet(ip, port, USER_LOGIN, password, new_password) 
            or connect_ssh(ip, port, USER_LOGIN, password, new_password)
        )

        result = {
            "ip": ip,
            "old_password": password,
            "new_password": new_password,
            "changed": password_changed,
        }
        results.append(result)

    create_results_file(results)
    logInfo.info("Скрипт выполнен")

if __name__ == "__main__":
    main()
