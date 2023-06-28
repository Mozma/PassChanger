1. Для работы нужно установить следующие библиотеки:
    pip install openpyxl
    pip install paramiko
    pip install telnetlib

2. Параметры запуска:
    Команда: 
        passchanger.py [-whatif] excel_file.xlsx passwords.txt
    Параметры:
        -whatif             Пробует просто подключиться используя полученные пароли. Логирует результат
        excel_file.xlsx     Путь до excel файла с паролями и ip адресами
        passwords.txt       Путь до текстового файла с паролями

