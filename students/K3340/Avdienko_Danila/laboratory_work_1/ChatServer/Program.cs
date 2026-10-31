using System.Net;
using System.Net.Sockets;
using System.Text;

Socket serverSocket = new Socket(
    AddressFamily.InterNetwork,
    SocketType.Stream,
    ProtocolType.Tcp
);

Dictionary<string, Socket> clients = new();
object clientsLock = new();

IPEndPoint serverEndPoint = new IPEndPoint(IPAddress.Loopback, 11002);
serverSocket.Bind(serverEndPoint);
serverSocket.Listen(10);

Console.WriteLine("Чат-сервер запущен на 127.0.0.1:11002");
while (true) // после подключения возвращаемся к аксепт и ждем новое подключение
{
    Socket clientSocket = serverSocket.Accept();
    Console.WriteLine($"Подключили клиент: {clientSocket.RemoteEndPoint}");
    Thread clientThread = new Thread(() => HandleClient(clientSocket)); // отдельный поток для каждого подключения (клиента)
    clientThread.Start();
}

void HandleClient(Socket clientSocket) // принимаем имя клиента, обрабатываем его сообщения, отправляем другим клиентам
{
    byte[] buffer = new byte[1024];
    int receivedBytes = clientSocket.Receive(buffer);

    string userName = System.Text.Encoding.UTF8.GetString(
        buffer,
        0,
        receivedBytes
    );
    lock (clientsLock) // блокируем доступ к коллекции clients:
// пока текущий поток находится внутри этого lock,то
// другие потоки не могут войти в блоки с тем же clientsLock
    {
        clients[userName] = clientSocket;
    }
    Console.WriteLine($"Подключился пользователь: {userName}");
    while (true)
    {
        receivedBytes = clientSocket.Receive(buffer);

        string message = Encoding.UTF8.GetString(
            buffer,
            0,
            receivedBytes
        );
        if (message == "/exit")
        {
            break;
        }
        string fullMessage = $"{userName}: {message}";
        Console.WriteLine(fullMessage);
        byte[] messageBytes = Encoding.UTF8.GetBytes(fullMessage);

        lock (clientsLock) // ставим лок, чтобы во время перебора никто не записался в словарь
        {
            foreach (var client in clients)
            {
                if (client.Value != clientSocket)
                {
                    client.Value.Send(messageBytes);
                }
            }
        }
    }
    lock (clientsLock)
    {
        clients.Remove(userName);
    }
    clientSocket.Close();
    Console.WriteLine($"Пользователь {userName} вышел из чата");
}