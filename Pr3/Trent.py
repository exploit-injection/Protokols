from socket import socket, SOCK_STREAM, AF_INET
import random
import sympy
import logging


# Функция генерации простых чисел
def gener(min_num, max_num):
    test = 10
    while not (sympy.isprime(test)):  # Проверка на простоту числа
        test = random.randint(min_num, max_num)  # Определение границ числа
    return test


def main():
    file_log = logging.FileHandler('py_log.log')  # Добавить параметр mode
    console_out = logging.StreamHandler()
    logging.basicConfig(handlers=(file_log, console_out),
                        format='[%(asctime)s | %(levelname)s]: %(message)s',
                        datefmt='%m.%d.%Y %H:%M:%S',
                        level=logging.INFO)

    # Соединение
    host = "localhost"
    port_peggy = 11113
    port_victor = 11111
    socket_peggy = socket(AF_INET, SOCK_STREAM)
    socket_peggy.bind((host, port_peggy))
    socket_peggy.listen(1)
    client_peggy, addr_peggy = socket_peggy.accept()
    socket_victor = socket(AF_INET, SOCK_STREAM)
    socket_victor.bind((host, port_victor))
    socket_victor.listen(1)
    client_victor, addr_victor = socket_victor.accept()

    # Генерация ключей
    bytes_gen = 100
    border = pow(2, bytes_gen)  # Создание границы для простого числа
    q = gener(border, 16 * border)
    logging.info(f'q: {q}')
    p = gener(border, 16 * border)
    logging.info(f'p: {p}')
    n = p * q
    logging.info(f'n: {n}')
    phi_n = (p - 1) * (q - 1)  # Функция Эйлера
    logging.info(f'phi(n): {phi_n}')
    e = gener(1, phi_n)
    logging.info(f'e: {e}')
    s = pow(e, -1, phi_n)
    logging.info(f's: {s}')
    hash_of_secret = client_peggy.recv(1000000)  # получаем хэш секрета
    j = int.from_bytes(hash_of_secret, "big", signed=False)  # Возврат числа из строки байтов
    logging.info(f'J: {j}')
    x = pow(j, -s, n)
    logging.info(f'x: {x}')
    y = pow(x, e, n)
    logging.info(f'y: {y}')
    message_to_peggy = str(n) + '!' + str(e) + '!' + str(x)
    client_peggy.send(message_to_peggy.encode('utf-8'))
    message_to_victor = str(n) + '!' + str(e) + '!' + str(y)
    client_victor.send(message_to_victor.encode('utf-8'))

    socket_victor.close()
    socket_peggy.close()


if __name__ == '__main__':
    main()
