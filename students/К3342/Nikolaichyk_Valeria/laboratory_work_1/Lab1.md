## Практическое задание 1. Обмен сообщениями по UDP

1. Создаю папку в pycharm с файлами server и client
<img width="308" height="204" alt="image" src="https://github.com/user-attachments/assets/3b43a79f-4ff5-408b-80ad-5071550d7761" />

2. импортирую библиотеку с сокетами в файл сервера 
<img width="205" height="48" alt="image" src="https://github.com/user-attachments/assets/6178d16d-912a-43c9-a313-4da8ae815291" />


3. создаю udp сокет и сохраняю в переменную 
<img width="485" height="56" alt="image" src="https://github.com/user-attachments/assets/c7f40b83-e560-4559-8fe6-1f67905d4883" />


4.  привязываю сокет к адресу и порту, где 127.0.0.1 это мой компьютер, а 5000 это порт 
<img width="479" height="158" alt="image" src="https://github.com/user-attachments/assets/a61101a2-fd67-4fc8-94ce-2c61a3e26bad" />


5. добавление команды ожидания сообщения, теперь в дата будет поступать сообщение, а в адрес адрес отправителя 
<img width="483" height="230" alt="image" src="https://github.com/user-attachments/assets/3770175c-ae23-4f99-b090-3fe44edb9df9" />


6.  Теперь делаю файл клиент, импортирую сокеты и создаю udp сокет клиента 
<img width="537" height="130" alt="image" src="https://github.com/user-attachments/assets/821867eb-9027-46c4-b7bb-eab5b5c8f2e8" />


7. создаю адрес куда отправлять сообщение и сам сообщение  
<img width="358" height="82" alt="image" src="https://github.com/user-attachments/assets/c0e0ecb1-ed01-4a64-b2b1-3d187f5fd23f" />
 
8. отправляю сообщение с помощью команды sendto, превращая сообщение в байты, т.к. сокет работает с байтами 
<img width="484" height="145" alt="image" src="https://github.com/user-attachments/assets/08fe3ec1-81ea-456a-a5ff-c4a0ad45705c" />

9. добавляю вывод сообщение в сервер 
<img width="279" height="56" alt="image" src="https://github.com/user-attachments/assets/d4524f79-ecec-4f8c-b322-f46e093939ec" />

10.  сервер получил сообщение 
<img width="876" height="79" alt="image" src="https://github.com/user-attachments/assets/0cd7a105-f903-43e6-a5a6-f54677514b59" />

11. добавляю ответ от сервера и принятие сообщения у клиента 
<img width="529" height="298" alt="image" src="https://github.com/user-attachments/assets/2a89211d-f05f-4057-b21d-053ca6249a19" />

<img width="551" height="285" alt="image" src="https://github.com/user-attachments/assets/c2d13fd7-bdab-42bf-977f-6dfa7b1a207e" />


12. проверка сервер получил ответ и клиент получил ответ.
<img width="672" height="139" alt="image" src="https://github.com/user-attachments/assets/26ce455a-128b-4d8f-abc0-4fdcd3595ed3" />

<img width="704" height="55" alt="image" src="https://github.com/user-attachments/assets/9adecd18-2dfc-4b99-b835-1c3b7ae39f5a" />


## Практическое задание 2.  Вычисления через TCP

У меня вариант 2 - Решение квадратного уравнения

1. делаю чтобы соединение было TCP и пишу socket.SOCK_STREAM
<img width="489" height="98" alt="image" src="https://github.com/user-attachments/assets/bedad86c-f372-4121-93e3-718fb830fbaf" />

2. Привязываю сокет к адресу и порту, слушаю входящие подключения, принимаю соединение от клиента, получаю сообщение, разделяю коэффициенты у переменных и считаю квадратный корень, отправляю полученные числа клиенту и закрываю соединение 
```python
import socket  
import math  
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
  
server_socket.bind(("localhost", 8080))  
server_socket.listen(1)  
  
print("Сервер запущен на порту 8080...")  
  
while True:  
    client_connection, client_address = server_socket.accept()  
    print(f'Подключение от {client_address}')  
  
    request = client_connection.recv(1024).decode()  
    a,b,c = map(float, request.split())  
    d = b*b - 4*a*c  
    x1 = (-b+math.sqrt(d))/(2*a)  
    x2 = (-b-math.sqrt(d))/(2*a)  
  
    print(f'корни уравнения будут {x1} и {x2}')  
    response = f'корни уравнения будут {x1} и {x2}'  
    client_connection.sendall(response.encode())  
  
    client_connection.close()
```

3.  создаю сокет, подключаюсь к серверу, отправляю числа и получаю ответ, закрываю соединение
```python
import socket  
  
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
  
client_socket.connect(('localhost', 8080))  
  
client_socket.sendall(b'1 -5 6')  
  
response = client_socket.recv(1024)  
print(f'Ответ от сервера: {response.decode()}')  
   
client_socket.close()
```

4. Запуск сервера и клиента, всё работает верно 
<img width="886" height="785" alt="image" src="https://github.com/user-attachments/assets/a6cfb528-8409-4fcb-acc9-faf5299e1a04" />

<img width="714" height="74" alt="image" src="https://github.com/user-attachments/assets/d6e446fb-6c01-4a0f-a68c-7e45e54a15fa" />




## Практическое задание 3. Раздача HTML-страницы по HTTP

1. создаю новый файл импортирую сокет, создаю параметры сервера, создаю сокет, привязываю сокет к адресу и порту, начинаю слушать входящее соединения
<img width="770" height="298" alt="image" src="https://github.com/user-attachments/assets/87770b29-a976-4905-8628-05b525d0f9b2" />



2. затем открываю index.html и считываю его содержимое в переменную html_content 
<img width="527" height="79" alt="image" src="https://github.com/user-attachments/assets/7ae452a9-9ca8-4829-b029-5a48980115ce" />


3.  Принимаю соединение от клиента, Получаем запрос от клиента, Формируем HTTP-ответ в котором байты я считаю с помощью encode("utf-8") т.к. буквы русские могут весить по-разному. Затем отправляю HTTP-ответ клиенту и закрываю соединение
<img width="656" height="740" alt="image" src="https://github.com/user-attachments/assets/bd4970f3-cbce-44b9-9186-16ef7d260894" />


4. В  index.html  оставляю текст из примера 
<img width="788" height="342" alt="image" src="https://github.com/user-attachments/assets/d0f79585-2172-4b88-a6ae-a62efdf4a20c" />


5. Проверяю что все работает
<img width="967" height="200" alt="image" src="https://github.com/user-attachments/assets/c5a11a3f-0c18-476b-8e37-5a090d136786" />

## Практическое задание 4. Чат на сокетах

Подключаю библиотеки и создаю сокет  и подключаю сервер. Пользователей подключённых храню в словаре
<img width="680" height="203" alt="image" src="https://github.com/user-attachments/assets/59a755e7-8f64-49d3-b510-607a18b1700d" />


Для работы с каждым клиентом делаю функцию в которой получаю имя пользователя и сохраняю его, затем запускаю цикл который будет принимать сообщения пока пользователь не отключится  и так же в этом цикле принимаю сообщения и отправляю другим пользователям кроме того который пишет
<img width="699" height="570" alt="image" src="https://github.com/user-attachments/assets/d992f159-4370-492d-b387-be1e67d64078" />


Создаю отдельный поток для каждого нового пользователя
<img width="909" height="217" alt="image" src="https://github.com/user-attachments/assets/8a19e22c-cbf6-4a6c-af2f-df1aff80932c" />


Затем для клиента создаю сокет и после подключения пользователь вводит свое имя 
<img width="584" height="205" alt="image" src="https://github.com/user-attachments/assets/2f709862-ac39-4b96-a65d-d7ee6e89ef69" />


функция получения сообщения от сервера с  циклом 
<img width="579" height="265" alt="image" src="https://github.com/user-attachments/assets/d911ae13-8c40-4cb6-95b7-6ae0c746c0c9" />


Для получения сообщения создается отдельный потом так как пользователь должен одновременно и получать сообщение и отправлять.
Пока пользователь не напишет /выход будет работать цикл 
<img width="562" height="272" alt="image" src="https://github.com/user-attachments/assets/169b56dc-6baf-4086-a2f7-87857e61f77d" />

## Практическое задание 5. Простой веб-сервер (GET/POST)

Для хранения оценок использую словарь: 
<img width="127" height="52" alt="image" src="https://github.com/user-attachments/assets/ae84c712-aefa-4ad0-822f-a5eb6e5dc9e6" />


Для обработки URL кодирования использую
<img width="292" height="48" alt="image" src="https://github.com/user-attachments/assets/54d1b941-6a81-4b3e-93df-68217acd4faa" />


Сначала создаю функцию для хранения и записи оценок
<img width="336" height="113" alt="image" src="https://github.com/user-attachments/assets/acb97362-b2a7-4b4e-9399-fb9d80618ae9" />


затем функцию html страницы, с формой для добавления новых оценок и вывод всех предметов с оценками 
<img width="644" height="519" alt="image" src="https://github.com/user-attachments/assets/819e3a09-0a93-4b79-a070-1b88d897e81d" />


Дальше пока верно запускаю цикл в котором подключаю клиеента и разделяю метод 
<img width="572" height="263" alt="image" src="https://github.com/user-attachments/assets/6826cfcc-c981-49e0-891b-0b419868f302" />



Затем разделяю проверку get и post запроса, в get  формирую html страницу с текущим журналом 
<img width="628" height="336" alt="image" src="https://github.com/user-attachments/assets/e49b63c8-fa7f-42ab-9e4f-d187c8969956" />


В post после отправки формы предмет и оценка сервер получает тело запроса, а потом разделяет данные и добавляет в журнал и заново создается html страница 
<img width="658" height="481" alt="image" src="https://github.com/user-attachments/assets/94c19e5e-902e-48fb-b7e7-6b9663c8516d" />
