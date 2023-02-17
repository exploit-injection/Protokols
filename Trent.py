from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import random
import string

# Создание ключей
secret_key = RSA.generate(2048)
public_key = secret_key.publickey()

# Экспорт
exp_public = public_key.export_key()
exp_public_string = exp_public.decode("utf-8")
print('Открытый ключ Трента: ')
print(exp_public_string)

# Соединение и обмен ключами
socket_alice = socket(AF_INET, SOCK_STREAM)
socket_alice.bind(('localhost', 11113))
socket_alice.listen(1)
client_alice, addr_alice = socket_alice.accept()
data = client_alice.recv(1000000) # получение ключа от Алисы
alice_public = RSA.importKey(data) # извлечение ключа
print('Открытый ключ Алисы: ')
print(data.decode('utf-8'))
socket_bob = socket(AF_INET, SOCK_STREAM)
socket_bob.bind(('localhost', 11112))
socket_bob.listen(1)
client_bob, addr_bob = socket_bob.accept()
client_bob.send(exp_public_string.encode('utf-8')) # Отправка ключа Трента Бобу
data = client_bob.recv(1000000) # получение ключа Боба
bob_public = RSA.importKey(data) #извлечение ключа
print('Открытый ключ Боба: ')
print(data.decode('utf-8'))

# Протокол
second_name = client_bob.recv(1000000) # Получение идентификатора Боба
print('Идентификатор Боба: ')
second_name = second_name.decode("utf-8")
print(second_name)
data = client_bob.recv(1000000) # Получение зашифрованного сообщения Боба
decryptor = PKCS1_OAEP.new(secret_key)
decrypted = decryptor.decrypt(data) # Расшифрование сообщения Боба
first_name, first_random, second_random = decrypted.decode("utf-8").split('!') # Разделение сообщения на 3 части
print('Идентификатор Алисы: '+first_name)
print('Случайное число Алисы: '+first_random)
print('Случайное число Боба: '+second_random)
letters = string.ascii_lowercase # генерация сессионного ключа
session_key = ''.join(random.choice(letters) for i in range(16))
print('Сессионный ключ: '+session_key)
# 3 этап - Создание 2-х сообщений Алисе
message = second_name+'!'+session_key+'!'+first_random+'!'+second_random # создание 1-го сообщения для Алисы
encryptor = PKCS1_OAEP.new(alice_public)
bit_message = message.encode('utf-8')
encrypted = encryptor.encrypt(bit_message) # Шифрование Б, К, сл. числа А, сл. числа Б
data = client_alice.recv(1000000) # синхронизация
client_alice.send(encrypted) # Отправление 1-го шифрованного сообщения Алисе
message = first_name+'!'+session_key # Создание 2-го сообщения Алисе
encryptor = PKCS1_OAEP.new(bob_public)
bit_message = message.encode('utf-8')
encrypted = encryptor.encrypt(bit_message) # Шифрование А, К для отправки Алисе
data1 = client_alice.recv(1000000) # синхронизация
client_alice.send(encrypted) # Отправляение 2-го шифрованного сообщения Алисе

# Закрытие
socket_alice.close()
socket_bob.close()