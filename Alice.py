from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# Создание ключей
secret_key = RSA.generate(2048)
public_key = secret_key.publickey()

# Экспорт
exp_public = public_key.export_key()
exp_public_string = exp_public.decode("utf-8")
print('Открытый ключ Алисы: ')
print(exp_public_string)

# Соединение и обмен ключами
socket_trent = socket(AF_INET, SOCK_STREAM)
socket_trent.connect(('localhost', 11113))
socket_trent.send(exp_public_string.encode('utf-8')) # Отправка ключа Алисы Тренту
socket_bob = socket(AF_INET, SOCK_STREAM)
socket_bob.bind(('localhost', 11111))
socket_bob.listen(1)
client_bob, addr_bob = socket_bob.accept()

# Протокол
alice_random=str(random.randint(0, 72817281)) # Создание сл. числа А
message = 'Alice'+'!'+alice_random # Создание сообщения для отправки Бобу
print('Идентификатор Алисы: '+'Alice')
# 1 этап - Передача Бобу идентификатора А и случайного числа А
client_bob.send(message.encode('utf-8'))
print('Случайное число Алисы: '+alice_random)
socket_trent.send('1'.encode('utf-8')) # Синхронизация
data = socket_trent.recv(1000000) # Получение данных от Трента
decryptor = PKCS1_OAEP.new(secret_key)
decrypted = decryptor.decrypt(data) # Расшифрование первого сообщения от Трента
second_name, session_key, first_random, second_random = decrypted.decode("utf-8").split('!') # Разделение сообщения на 4 части
print('Полученный идентификатор Боба: '+second_name)
print('Извлеченный сессионный ключ: '+session_key)
print('Полученное от Трента случайное число Алисы: '+first_random)
print('Полученное от Трента случайное число Боба: '+second_random)
socket_trent.send('1'.encode('utf-8')) # Синхронизация
data = socket_trent.recv(1000000) # Получение 2-го сообщения от Трента
# 4 этап - Отправка сообщений Бобу
client_bob.send(data) # Отправление сообщения Бобу
cipher = AES.new(session_key.encode('utf8'), AES.MODE_ECB) # Формирование ключа для шифрования 2-го сообщения от Алисы (ключ, режим)
second_random = second_random.encode('utf8')
encrypted = cipher.encrypt(pad(second_random, 32)) # Шифрование сл. числа Б на сессионном ключе
client_bob.send(encrypted) # Отправление сообщения Бобу

# Закрытие
socket_bob.close()
socket_trent.close()