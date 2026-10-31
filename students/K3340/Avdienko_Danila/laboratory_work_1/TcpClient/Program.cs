using System.Net;
using System.Net.Sockets;
using System.Text;

Socket clientSocket = new Socket(
    AddressFamily.InterNetwork,
    SocketType.Stream,
    ProtocolType.Tcp
);

EndPoint serverEndPoint = new IPEndPoint(IPAddress.Loopback, 11001);
clientSocket.Connect(serverEndPoint);

Console.Write("Введите первый катет: ");
double a = double.Parse(Console.ReadLine()!);
Console.Write("Введите второй катет: ");
double b = double.Parse(Console.ReadLine()!);
string message = $"{a} {b}";
byte[] data = Encoding.UTF8.GetBytes(message);

clientSocket.Send(data);

byte[] buffer = new byte[1024];
int receivedBytes = clientSocket.Receive(buffer);
string response = Encoding.UTF8.GetString(buffer, 0, receivedBytes);
Console.WriteLine($"Гипотенуза: {response}");

clientSocket.Close();