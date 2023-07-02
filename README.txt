1. Для работы нужно установить следующие библиотеки:
    pip install openpyxl
    pip install paramiko
    pip install telnetlib

2. Параметры запуска:
    Команда: 
        PassChanger.py [-whatif] <excel_file> <passwords_file>
    Параметры:
        -whatif             Пробует просто подключиться используя полученные пароли. Логирует результат
        <excel_file>        Путь до excel файла с паролями и ip адресами
        <passwords_file>    Путь до текстового файла с новыми паролями

