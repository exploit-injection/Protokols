from socket import socket, SOCK_STREAM, AF_INET
import random
import logging


def main():
    logging.basicConfig(format='[%(asctime)s | %(levelname)s]: %(message)s',
                        datefmt='%m.%d.%Y %H:%M:%S',
                        level=logging.INFO)

    # Соединение
    host = 'localhost'
    port_trent = 11111
    port_peggy = 11112
    socket_trent = socket(AF_INET, SOCK_STREAM)
    socket_trent.connect((host, port_trent))
    socket_peggy = socket(AF_INET, SOCK_STREAM)
    socket_peggy.connect((host, port_peggy))

    # Генерация ключей
    data_bytes = 1000000
    open_key = socket_trent.recv(data_bytes)  # Получение открытого ключа от Трента
    n, e, y = open_key.decode("utf-8").split('!')
    n = int(n)
    logging.info(f'n: {n}')
    e = int(e)
    logging.info(f'e: {e}')
    y = int(y)
    logging.info(f'y: {y}')

    # Протокол
    data = socket_peggy.recv(data_bytes)  # Получение параметра а от Пегги
    a = int.from_bytes(data, byteorder="big")
    logging.info(f'a: {a}')
    c = random.randint(1, e - 1)
    logging.info(f'c: {c}')
    socket_peggy.send(c.to_bytes((c.bit_length() + 7) // 8, 'big'))  # Отправление параметра c Пегги
    data = socket_peggy.recv(data_bytes)  # Получение параметра z от Пегги
    z = int.from_bytes(data, byteorder="big")
    logging.info(f'z: {z}')
    first = pow(z, e, n)
    logging.info(f'Первый параметр: {first}')
    second = (a * pow(y, c, n)) % n
    logging.info(f'Второй параметр: {second}')
    if first == second:
        logging.info("Идентификация пройдена успешно!!!")
    else:
        logging.info("Я не верю, что это Пегги")

    # Закрытие
    socket_trent.close()
    socket_peggy.close()


if __name__ == '__main__':
    main()
