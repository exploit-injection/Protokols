from socket import socket, SOCK_STREAM, AF_INET
import random
import sympy
import hashlib
import logging


def gener(max_num, min_num):
    test = 10
    while not (sympy.isprime(test)):
        test = random.randint(max_num, min_num)
    return test


def main():
    logging.basicConfig(format='[%(asctime)s | %(levelname)s]: %(message)s',
                        datefmt='%m.%d.%Y %H:%M:%S',
                        level=logging.INFO)

    # Соединение
    HOST = "localhost"
    port_trent = 11113
    port_victor = 11112
    socket_trent = socket(AF_INET, SOCK_STREAM)
    socket_trent.connect((HOST, port_trent))
    socket_victor = socket(AF_INET, SOCK_STREAM)
    socket_victor.bind((HOST, port_victor))
    socket_victor.listen(1)
    client_victor, addr_victor = socket_victor.accept()

    # Генерация ключей
    logging.info('Введите вашу секретную строку: ')
    secret_string = input()
    md5_hash = hashlib.md5()  # Выбор доступного алгоритма хэширования из библиотеки hashlib
    md5_hash.update(secret_string.encode('utf-8'))  # Хэширование и кодировка строки
    hash_of_secret = md5_hash.digest()  # Получение байтовых данных
    socket_trent.send(hash_of_secret)  # Передача Тренту секретного хэша
    j = int.from_bytes(hash_of_secret, "big", signed=False)  # Возврат числа из строки байтов
    logging.info(f'J: {j}')
    bytes_data = 1000000
    open_key = socket_trent.recv(bytes_data)  # Получение открытого ключа
    n, e, x = open_key.decode("utf-8").split('!')
    # n, e, x = [int(i) for i in open_key.decode("utf-8").split('!')]
    n = int(n)
    logging.info(f'n: {n}')
    e = int(e)
    logging.info(f'e: {e}')
    x = int(x)
    logging.info(f'x: {x}')

    # Протокол
    r = random.randint(1, int(n) - 1)
    logging.info(f'r: {r}')
    a = pow(r, e, n)
    logging.info(f'a: {a}')
    client_victor.send(a.to_bytes((a.bit_length() + 7) // 8, 'big'))  # Отправление параметра a Виктору
    data = client_victor.recv(bytes_data)  # получение параметра c от Виктора
    c = int.from_bytes(data, byteorder="big")
    logging.info(f'c: {c}')
    z = (r * pow(x, c, n)) % n
    logging.info(f'z: {z}')
    client_victor.send(z.to_bytes((z.bit_length() + 7) // 8, 'big'))  # Передача параметра z Виктору

    # Закрытие
    client_victor.close()
    socket_trent.close()


if __name__ == '__main__':
    main()
