using System.Net;
using System.Net.Sockets;
using System.Text;

Socket serverSocket = new Socket(
    AddressFamily.InterNetwork,
    SocketType.Stream,
    ProtocolType.Tcp
);
Dictionary<string, List<int>> grades = new(); // словарь для записей
EndPoint serverEndPoint = new IPEndPoint(IPAddress.Loopback, 8071);
serverSocket.Bind(serverEndPoint);
serverSocket.Listen(10);
Console.WriteLine("HTTP сервер запущен на http://127.0.0.1:8071");

while (true) // цикл обработки подключения и его get/post запросов
{
    Socket clientSocket = serverSocket.Accept();// принимаем новое TCP-соединение
    Console.WriteLine($"Подключился клиент: {clientSocket.RemoteEndPoint}");
    byte[] buffer = new byte[4096]; // буфер для полученного HTTP-запроса

    int receivedBytes = clientSocket.Receive(buffer);
    string request = Encoding.UTF8.GetString(buffer, 0, receivedBytes);
    if (request.StartsWith("POST") && request.Split("\r\n\r\n")[1] == "") // если POST пришёл без тела, то дочитываем его отдельно
    {
        receivedBytes = clientSocket.Receive(buffer);
        request += Encoding.UTF8.GetString(buffer, 0, receivedBytes);
    }
    
    if (request.StartsWith("GET")) // get-request
    {
        string gradeList = ""; // создаем строку для передачи в html-код
        foreach (var subject in grades)
        {
            gradeList += $"<p>{subject.Key}: {string.Join(", ", subject.Value)}</p>"; // циклом создаем строки из всех записей словаря 
        }
        string html = $"""
                      <!DOCTYPE html>
                      <html lang="ru">
                      <head>
                          <meta charset="UTF-8">
                          <title>Журнал оценок</title>
                      </head>
                      <body>
                          <h1>Журнал оценок</h1>
                          {gradeList}
                          <form method="POST" action="/grade">
                              <label>Предмет:</label>
                              <input type="text" name="subject">
                      
                              <label>Оценка:</label>
                              <input type="number" name="grade">
                      
                              <button type="submit">Добавить</button>
                          </form>
                      </body>
                      </html>
                      """;

        byte[] htmlBytes = Encoding.UTF8.GetBytes(html);

        string headers =
            "HTTP/1.1 200 OK\r\n" +
            "Content-Type: text/html; charset=UTF-8\r\n" +
            $"Content-Length: {htmlBytes.Length}\r\n" +
            "Connection: close\r\n" +
            "\r\n";

        clientSocket.Send(Encoding.UTF8.GetBytes(headers + html));
    }
    else if (request.StartsWith("POST")) // обработка пост-запроса
    {
        string body = request.Split("\r\n\r\n")[1]; // получаем тело запроса
        string[] data = body.Split('&'); // получаем отдельно поля subject и grade

        string subject = data[0].Split('=')[1]; // парсим значения полей
        int grade = int.Parse(data[1].Split('=')[1]);

        if (!grades.ContainsKey(subject)) // создаем новую запись при необходимости
            grades[subject] = new List<int>();

        grades[subject].Add(grade);

        clientSocket.Send(Encoding.UTF8.GetBytes( // отправляем браузеру команду заново открыть стартовую страницу
            "HTTP/1.1 303 See Other\r\nLocation: /\r\n\r\n"
        ));
        Console.WriteLine(body);
    }
    clientSocket.Close();
}