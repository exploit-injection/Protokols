from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# Генерация закрытого и открытого ключей
secret_key = RSA.generate(2048)
public_key = secret_key.publickey()

# Формирование ключа для отправки на сервер
# Возврат закодированного ключа в вид байтовой строки
export_public = public_key.export_key() # PEM - Кодирование текста в соответствии с RFC1421/RFC1423.
# Перевод закодированных символов в однобайтовые единицы
export_public_str = export_public.decode("utf-8")
print('Открытый ключ сервера: ')
print(export_public_str)

# Соединение и обмен ключами
s = socket(AF_INET, SOCK_STREAM) # Создаем сокет TCP, AF_INET--коммуникационный домен
s.bind(('', 9090)) # Связываем сокет с хостом и портом
s.listen(1) # Режим прослушивания, одно подключение в очереди - клиент
client, addr = s.accept() # Прием запроса на соединение и посылка данных клиенту
data = client.recv(1000000) # Получаем кол-во байт от клиента (ключ)
client_public = RSA.importKey(data) # Извлекаем ключ клиента
client.send(export_public_str.encode('utf-8')) # Отправляем открытый ключ клиенту
print('Открытый ключ клиента: ')
print(data.decode("utf-8"))

# Обмен сообщениями
print('Сообщение,отправляемое клиенту: ')
message = input()
# Представление ключа - его формат
encryptor = PKCS1_OAEP.new(client_public)
bit_message = message.encode('utf-8')
encrypted = encryptor.encrypt(bit_message)
enc_first_part = encrypted[:len(encrypted)//2] # деление на две части
enc_second_part = encrypted[len(encrypted)//2:]
client_first_part = client.recv(1000000)
print('Первая часть сообщения клиента:')
print(client_first_part.decode("utf-8", errors='ignore'))
client.send(enc_first_part)
print('Первая часть сообщения сервера:')
print(enc_first_part.decode("utf-8", errors='ignore'))
client_second_part = client.recv(1000000)
print('Вторая часть сообщения клиента:')
print(client_second_part.decode("utf-8", errors='ignore'))
client.send(enc_second_part)
print('Вторая часть сообщения сервера:')
print(enc_second_part.decode("utf-8", errors='ignore'))
encrypted_data=client_first_part+client_second_part

# Расшифровка
decryptor = PKCS1_OAEP.new(secret_key)
decrypted = decryptor.decrypt(encrypted_data)
answer = decrypted.decode("utf-8")
print('Ответ от клиента:')
print(answer)
client.close() # закрываем соединение с клиентом