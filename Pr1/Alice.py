from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# Генерация закрытого и открытого ключей
secret_key = RSA.generate(2048)
public_key = secret_key.publickey()

# Формирование ключа для отправки на сервер
# Возврат закодированного ключа в вид байтовой строки
export_public = public_key.export_key() # PEM - Кодирование текста в соответствии с RFC1421/RFC1423.
# Перевод закодированных символов в строку однобайтовых единиц
export_public_str = export_public.decode("utf-8")
print('Открытый ключ клиента: ')
print(export_public_str)

# Соединение и обмен ключами
s = socket(AF_INET, SOCK_STREAM)  # Создаем сокет TCP. Коммуникационная поддержка
s.connect(('localhost', 9090))  # Соединяем клиента с сервером
s.send(export_public_str.encode('utf-8'))  # передаем открытый ключ клиента, строка
data = s.recv(1000000)  # получаем ключ сервера
server_public = RSA.importKey(data) # извлечение ключа
print('Открытый ключ сервера: ')
print(data.decode("utf-8"))

# Обмен сообщениями
print('Сообщение, отправляемое серверу: ')
message = input()
# PKCS#1 OAEP — асимметричный шифр, основанный на RSA
encryptor = PKCS1_OAEP.new(server_public)
bit_message = message.encode('utf-8')
encrypted = encryptor.encrypt(bit_message)
enc_first_part = encrypted[:len(encrypted)//2] # деление на две части
enc_second_part = encrypted[len(encrypted)//2:]
s.send(enc_first_part)
print('Перваая часть сообщения клиента:')
print(enc_first_part.decode("utf-8", errors='ignore')) # игнорирование ошибки при декодировании
serv_first_part = s.recv(1000000)
print('Первая часть сообщения сервера:')
print(serv_first_part.decode("utf-8", errors='ignore'))
s.send(enc_second_part)
print('Вторая часть сообщения клиента:')
print(enc_second_part.decode("utf-8", errors='ignore'))
serv_second_part = s.recv(1000000)
print('Вторая часть сообщения сервера:')
print(serv_second_part.decode("utf-8", errors='ignore'))
encrypted_data =serv_first_part+serv_second_part

# Расшифровка
decryptor = PKCS1_OAEP.new(secret_key)
decrypted = decryptor.decrypt(encrypted_data)
answer = decrypted.decode("utf-8")
print('Ответ от сервера:')
print(answer)
s.close()
