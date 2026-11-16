## Простой веб-сервер (GET/POST)

> ### Дисклеймер:
> Это было самым слоным из заданий, для него я изучил практики, которые используются в реальной жизни, например изменение
> хранящего на сервере шаблона html-страницы. Помимо этого я столкнулся с трудностями в парсинге и искал способ решения,
> которым оказалась отдельная библиотека. Поэтому на это задание я потратил больше времени, чем планировал и просрочил дедлайн на день.
> В общем, прошу принять эту работу без решенного лит кода, на него уже нет сил)


---
> ### Задание:

> Написать простой веб-сервер для обработки GET и POST HTTP-запросов с помощью библиотеки socket в Python. Сервер должен:

> - Принимать и записывать информацию о дисциплине и оценке по дисциплине.

> - Отдавать информацию обо всех оценках по дисциплинам в виде HTML-страницы.

---
### Выполнение:

Перед началом работы я изучил реальные практики для предоставления страницы с обновленными данными.
В реальной жизни на серверах хранится ```шаблон html-страницы```, в нем есть переменная, которую можно изменять
в коде сервера.
---
### Подгтовка:

Я попросил нейронку написать мне код для красивой html-страницы, в котром будет содержатся такая переменная.

Я получил от Gemini такой вариант:

```
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <title>Электронный журнал оценок</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f9f9f9; color: #333; }
        h1, h2 { color: #2c3e50; }
        form { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); max-width: 400px; }
        input[type="text"], input[type="number"] { width: 100%; padding: 8px; margin: 8px 0 16px 0; box-sizing: border-box; }
        button { background-color: #3498db; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background-color: #2980b9; }
        ul { list-style-type: none; padding: 0; }
        li { background: white; padding: 10px 15px; margin-bottom: 8px; border-radius: 4px; border-left: 5px solid #2ecc71; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    </style>
</head>
<body>
    <h1>Электронный журнал</h1>
    
    <h2>Добавить новую оценку</h2>
    <form method="POST" action="/">
        <label for="subject">Дисциплина:</label>
        <input type="text" id="subject" name="subject" required placeholder="Например: Математика">
        
        <label for="mark">Оценка:</label>
        <input type="number" id="mark" name="mark" min="1" max="5" required placeholder="От 1 до 5">
        
        <button type="submit">Сохранить оценку</button>
    </form>

    <h2>Все оценки (сгруппированы по предметам):</h2>
    <ul>
        %MARKS_LIST%
    </ul>
</body>
</html>
```

Тут ```%MARKS_LIST%``` является переменной. Запомним это и в коде сервера будем собирать готовую страницу для отправки,
предварительно заменяя значение переменной на актуальной список оценок, хранящихся в словаре на сервере.

---
### Создание и бинд сокетов

Тут по стандарту, создаем серверный сокет, биндим на порт '9050' и ждем подключения:

```
import socket
from urllib.parse import parse_qs

marks_dict = {}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('', 9050))
server.listen(5)
print("Сервер поднят по адресу http://localhost:9050 и ждет запрос")
```

При этом сервер я писал ориентируясь на версию из задания 4. Но тут упрощенная версия без потоков, которая, тем не менее может работать с несколькими клиентами.

---
### Парсинг запроса:

После установления соединения и получение запроса от клиента, нужно понять, что клиент хочет от сервера.

- Переводим запрос в читаемый текст из байтов

- Делим запрос на заголовки и тело, ориентируясь на пустую строку, которая их разделяет
При этом надо помнить о мусорных пакетах от браузера и проверять их на каждой итерации деления.
На этом этапе единственное о чем нужно помнить - не у каждого запроса есть заголовки и тело. 
Например, запрос ```GET``` идет без тела, в этом случае читаем только заголовки, а в тело записываем пустоту.

- Далее работаем с заголовками. Нас интересует первая строка. Делим заголовок на строки 

- Берем первую строку заголовка и снова делим на части

- Берем первую часть - это и есть метод, который просит от нас клиент ```POST``` или ```GET```
Вот тут находится главный обработчик мусорных пакетов ```if len(parts) < 2:
    client_socket.close()
    print("Пришел мусорный пакет")
    continue``` 

> При проверке сервера оказалось, что все эти проверки - оверкилл, за все время тестрования браузер не отправил ни одного мусорного пакета

Код парсинга заголовка выглдяит так:

```
while True:
    client_socket, client_address = server.accept()
    
    try:
        raw_request = client_socket.recv(2048)
        if not raw_request:
            client_socket.close()
            continue

        client_request = raw_request.decode('utf-8')

        if '\r\n\r\n' in client_request:
            request_headers, request_body = client_request.split('\r\n\r\n', 1)
        else:
            request_headers = client_request
            request_body = ''

        request_headers_lines = request_headers.splitlines()
        if not request_headers_lines:
            client_socket.close()
            continue

        request_headers_line = request_headers_lines[0]
        parts = request_headers_line.split()

        if len(parts) < 2:
            client_socket.close()
            print("Пришел мусорный пакет")
            continue

        method = parts[0]
```

--- 
### Обработка метода POST

Если клиент просит внести оценку в словарь сервера (он создан еще до цикл while, забыл упомянуть), то нам надо распарсить тело запроса.
Тело приходит в HTML формате. Чтобы сделать текст тела читаемым используем библиотеку ```urllib.parse```, конкртено метод ```parse_qs```.
После паринга делим уже читаемое тело запроса на 2 переменные: ```subjects``` и ```marks```. По дефолту значения этих переменных приходят списками.
Поэтому обрезаем эти списки по первому элементу и получаем предмет и оценку за него. Если предмета, оценку за который требуется поставить нет в словаре оценок,
то добавляем его и сразу за ним оценку, если есть - то просто оценку в соответствующий ключ. И пишем сообщение на сервере о том, что оценка поставлена.
В конце по форме пишем свои ```headers``` для ответа и отправляем клиенту, чтобы код не завис на POST и не слоался при вызове GET. Как оказалось при 
написании и проверке, если не отправить клиенту эти заголовки и попытаться перезагрузить страницу, запрос на POST будет выполняться каждый раз, но перед
этим появиться предупреждение "Вы уверены, что хотите отправить форму заново?", это было неприятно, зато я теперь понимаю в каких случаях браузер предупреждает об этом.

Код этой части:

```
 if method == 'POST':
     parsed_body = parse_qs(request_body) # библиотека для парсинга html запросов
     subjects = parsed_body.get('subject')
     marks = parsed_body.get('mark')

     if subjects and marks:
         subject = subjects[0].strip()
         mark = marks[0].strip()
         
         if subject not in marks_dict:
             marks_dict[subject] = []
         marks_dict[subject].append(mark)
         print(f"Добавлена оценка {mark} по предмету {subject}")

         response_headers = (
             "HTTP/1.1 303 See Other\r\n"
             "Location: /\r\n"
             "Connection: close\r\n"
             "\r\n"
         )

         client_socket.sendall(response_headers.encode('utf-8'))
```

---
### Обработка метода GET

Тут я столкнулся с наибольшим количеством трудностей просто потому что постоянно забывал, что все сообщения клиенту нужно оборачивать в ```html``` формат.

Здесь я создаю пустую строку, в которой буду формировать список оценок в формате html. Циклом пробегаю по всем ключам и для каждого заполняю строку marks_html.
Если предметы пока не добавлены, то просто отправляю сообщение о необходимости ввести хотя бы какие-то оценки. Далее возвращаемся к шаблону, созданному на этапе подготовки.
Я читаю его и заменяю в нем переменную ```%MARKS_LIST``` на переменную marks_html, которая хранит строку с актуальными оценками. Далее снова заголовки для ответа по шаблону,
соединение заголовков с телом, в котром лежит строка оценок в html формате и код html страницы и отправка клиенту.

И в конце главного цикла остается только закрыть сокет и прервать подключение.

Код этой части:

```
    else:
        marks_html = ""
        for sub, list_of_marks in marks_dict.items():
            str_marks = ", ".join(list_of_marks)
            marks_html += f"<li><b>{sub}</b>: {str_marks}</li>"
        if not marks_html:
            marks_html = "<li>В журнале нет оценок, сначала добавьте их</li>"

        try:
            with open('marks.html', 'r', encoding='utf-8') as f:
                html_template = f.read()
        except FileNotFoundError:
            html_template = "<h1>Файл marks.html не найден на сервере</h1>"

        final_html = html_template.replace("%MARKS_LIST%", marks_html)
        response_final = final_html.encode('utf-8')

        response_headers = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(response_final)}\r\n"
            "Connection: close\r\n"
            "\r\n"
        )

        client_socket.sendall(response_headers.encode('utf-8') + response_final)
except Exception as e:
    print(f"Ошибка при обработке запроса {e}")

finally:
    client_socket.close()
```

---
### Код целиком для удобного чтения:

```
import socket
from urllib.parse import parse_qs

marks_dict = {}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('', 9050))
server.listen(5)
print("Сервер поднят по адресу http://localhost:9050 и ждет запрос")

while True:
    client_socket, client_address = server.accept()
    
    try:
        raw_request = client_socket.recv(2048)
        if not raw_request:
            client_socket.close()
            continue

        client_request = raw_request.decode('utf-8')

        if '\r\n\r\n' in client_request:
            request_headers, request_body = client_request.split('\r\n\r\n', 1)
        else:
            request_headers = client_request
            request_body = ''

        request_headers_lines = request_headers.splitlines()
        if not request_headers_lines:
            client_socket.close()
            continue

        request_headers_line = request_headers_lines[0]
        parts = request_headers_line.split()

        if len(parts) < 2:
            client_socket.close()
            print("Пришел мусорный пакет")
            continue

        method = parts[0]
        path = parts[1]

        if method == 'POST':
            parsed_body = parse_qs(request_body) # библиотека для парсинга html запросов
            subjects = parsed_body.get('subject')
            marks = parsed_body.get('mark')

            if subjects and marks:
                subject = subjects[0].strip()
                mark = marks[0].strip()
                
                if subject not in marks_dict:
                    marks_dict[subject] = []
                marks_dict[subject].append(mark)
                print(f"Добавлена оценка {mark} по предмету {subject}")

                response_headers = (
                    "HTTP/1.1 303 See Other\r\n"
                    "Location: /\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                )

                client_socket.sendall(response_headers.encode('utf-8'))

        else:
            marks_html = ""
            for sub, list_of_marks in marks_dict.items():
                str_marks = ", ".join(list_of_marks)
                marks_html += f"<li><b>{sub}</b>: {str_marks}</li>"
            if not marks_html:
                marks_html = "<li>В журнале нет оценок, сначала добавьте их</li>"

            try:
                with open('marks.html', 'r', encoding='utf-8') as f:
                    html_template = f.read()
            except FileNotFoundError:
                html_template = "<h1>Файл marks.html не найден на сервере</h1>"

            final_html = html_template.replace("%MARKS_LIST%", marks_html)
            response_final = final_html.encode('utf-8')

            response_headers = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                f"Content-Length: {len(response_final)}\r\n"
                "Connection: close\r\n"
                "\r\n"
            )

            client_socket.sendall(response_headers.encode('utf-8') + response_final)
    except Exception as e:
        print(f"Ошибка при обработке запроса {e}")

    finally:
        client_socket.close()
```

---
### Тестирование:

Поднимаю сервер. В браузере перехожу по его адресу, ввожу значения и смотрю на мгновенное обновление страницы.

Сторона клиента:

![alt text](<Screenshot 2026-10-02 143757.png>)

Сторона сервера:

![alt text](<Screenshot 2026-10-02 143803.png>)

----
Видим, что задание успешно выполнено. Клиент отправляет запросы POST с оценками и предметами, сервер обновляет словарь.
Сразу после клиент отправляет GET запрос и получает обновленную html-страницу с актуальными оценками.