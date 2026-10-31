using System.Net;
using System.Net.Sockets;
using System.Text;

Socket clientSocket = new Socket(
    AddressFamily.InterNetwork,
    SocketType.Stream,
    ProtocolType.Tcp
);

EndPoint serverEndPoint = new IPEndPoint(IPAddress.Loopback, 11002);
clientSocket.Connect(serverEndPoint);

// считываем и отправляем серверу имя клиента
Console.Write("Введите имя: ");
string userName = Console.ReadLine()!;
byte[] nameBytes = System.Text.Encoding.UTF8.GetBytes(userName);
clientSocket.Send(nameBytes);

Thread receiveThread = new Thread(() => ReceiveMessages(clientSocket));
receiveThread.Start();
Console.WriteLine("Подключение к чат-серверу установлено");

// отправляем сообщения на сервер
while (true)
{
    string message = Console.ReadLine()!;
    byte[] messageBytes = Encoding.UTF8.GetBytes(message);
    clientSocket.Send(messageBytes);

    if (message == "/exit")
    {
        break;
    }
}

clientSocket.Close();

void ReceiveMessages(Socket clientSocket) // метод для получения сообщений от других клиентов
{
    byte[] buffer = new byte[1024];
    try
    {
        while (true)
        {
            int receivedBytes = clientSocket.Receive(buffer);
            if (receivedBytes == 0)
            {
                break;
            }
            string message = Encoding.UTF8.GetString(
                buffer,
                0,
                receivedBytes
            );
            Console.WriteLine(message);
        }
    }
    catch (SocketException)
    {
    }
}