using System.Net;
using System.Net.Sockets;
using System.Text;

Socket serverSocket = new Socket(
    AddressFamily.InterNetwork,
    SocketType.Dgram,
    ProtocolType.Udp
);

EndPoint serverEndPoint = new IPEndPoint(IPAddress.Loopback, 11000);
serverSocket.Bind(serverEndPoint);
Console.WriteLine("UDP сервер запущен на эндпоинте 127.0.0.1:11000");

byte[] buffer = new byte[1024];

EndPoint clientEndPoint = new IPEndPoint(IPAddress.Any, 0);
int receivedBytes = serverSocket.ReceiveFrom(buffer, ref clientEndPoint);
string message = Encoding.UTF8.GetString(buffer, 0, receivedBytes);
Console.WriteLine($"Получено сообщение: {message}");

byte[] response = Encoding.UTF8.GetBytes("Привет, клиент!");
serverSocket.SendTo(response, clientEndPoint);
serverSocket.Close();