using System.Net;
using System.Net.Sockets;
using System.Text;

Socket clientSocket = new Socket(
    AddressFamily.InterNetwork,
    SocketType.Dgram,
    ProtocolType.Udp
);

IPEndPoint serverEndPoint = new IPEndPoint(IPAddress.Loopback, 11000);
byte[] message = Encoding.UTF8.GetBytes("Привет, сервер!");
clientSocket.SendTo(message, serverEndPoint);

byte[] buffer = new byte[1024];

EndPoint remoteEndPoint = new IPEndPoint(IPAddress.Any, 0);
int receivedBytes = clientSocket.ReceiveFrom(buffer, ref remoteEndPoint);
string response = Encoding.UTF8.GetString(buffer, 0, receivedBytes);
Console.WriteLine($"Получено сообщение: {response}");

clientSocket.Close();