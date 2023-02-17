from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import logging # Посмотреть
# Создание ключей
secret_key = RSA.generate(2048)
public_key = secret_key.publickey()

# Экспорт
exp_public = public_key.export_key()
exp_public_string = exp_public.decode("utf-8")
print('Открытый ключ Боба: ')
print(exp_public_string)
# Менеджер контекста with
# Соединение и обмен ключами
socket_alice = socket(AF_INET, SOCK_STREAM)
socket_alice.connect(('localhost', 11111))
socket_trent = socket(AF_INET, SOCK_STREAM)
socket_trent.connect(('localhost', 11112))
data = socket_trent.recv(1000000) # получение ключа Трента
trent_public = RSA.importKey(data) # извлечение ключа
socket_trent.send(exp_public_string.encode('utf-8')) # Отправка ключа Боба Тренту
print('Открытый ключ Трента: ')
print(data.decode("utf-8"))

# Протокол
data = socket_alice.recv(1000000) # Получение данных от Алисы
name, alice_random = data.decode("utf-8").split('!') # Разделение сообщения от Алисы на идентификатор и случайное число
bob_random=str(random.randint(0, 72817281)) # Создание случайного числа Боба
print(f'Полученное случайное число Алисы: {alice_random}') # Вывод случайного числа Алисы
message = 'Alice'+'!'+alice_random+'!'+bob_random # Объединение идентификатора А, сл. числа А и сл. числа Б
print('Случайное число Боба: '+bob_random)  # Вывод случайного числа Боба
socket_trent.send('Bob'.encode('utf-8')) # Отправка Тренту идентификатора Боба
encryptor = PKCS1_OAEP.new(trent_public) # 2 этап - Создание шифрованного сообщения Тренту
bit_message = message.encode('utf-8')
encrypted = encryptor.encrypt(bit_message) # Шифрование A, сл. числа A, сл. числа Б общим с Трентом ключом
socket_trent.send(encrypted) # Отправление шифрованного сообщения
data = socket_alice.recv(1000000) # Боб получает первое сообщение от Алисы
decryptor = PKCS1_OAEP.new(secret_key)
decrypted = decryptor.decrypt(data) # Расшифрование первого сообщения
first_name, session_key = decrypted.decode("utf-8").split('!') # Разделение сообщения на 2 части
print('Полученный идентификатор Алисы: '+first_name)
print('Полученный от Алисы сессионный ключ: '+session_key)
data = socket_alice.recv(1000000) # Боб получает второе сообщение от Алисы
decipher = AES.new(session_key.encode('utf8'), AES.MODE_ECB) # Подготовка ключа для расшифрования сообщения
decrypted_data = decipher.decrypt(data) # Расшифрование 2-го сообщения от Алисы
second_random = decrypted_data.decode("utf-8")
#decrypted_data = unpad(decrypted_data, 32)

print('Полученное от Алисы случайное число Боба:' +second_random[0:8])

# Закрытие
socket_alice.close()
socket_trent.close()
