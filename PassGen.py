import random
import string
import sys

def generate_password(length: int) -> str:
    """Генерирует случайный пароль заданной длины"""
    characters = string.ascii_uppercase + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def create_password_file(filename: str, password_count: int, password_length: int) -> None:
    """Создает файл с заданным количеством паролей заданной длины"""
    with open(filename, 'w', encoding='utf-8') as file:
        for i in range(password_count):
            if i != 0:
                file.write('\n')
            password = generate_password(password_length)
            file.write(password)

def main() -> None:
    if len(sys.argv) != 3:
        print('Usage: PassGen.py <password_length> <password_count>')
        sys.exit(1)

    password_length = int(sys.argv[1])
    password_count = int(sys.argv[2])

    filename = 'pwd.txt'

    create_password_file(filename, password_count, password_length)
    print(f'Успешно сгенерированно {password_count} паролей длинной {password_length} символов.')

if __name__ == '__main__':
    main()    