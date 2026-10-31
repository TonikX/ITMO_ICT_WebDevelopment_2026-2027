using System.Net;
using System.Net.Sockets;
using System.Text;

Socket serverSocket = new Socket(
    AddressFamily.InterNetwork,
    SocketType.Stream,
    ProtocolType.Tcp
);

EndPoint serverEndPoint = new IPEndPoint(IPAddress.Loopback, 11001);
serverSocket.Bind(serverEndPoint);
serverSocket.Listen(1);

Console.WriteLine("TCP сервер запущен на 127.0.0.1:11001");
Console.WriteLine("Ожидание клиента");

Socket clientSocket = serverSocket.Accept(); // создает сокет для общения
                                             // со следующим по очереди клиентом
byte[] buffer = new byte[1024];
int receivedBytes = clientSocket.Receive(buffer);

string message = Encoding.UTF8.GetString(buffer, 0, receivedBytes);
string[] values = message.Split(' ');
double a = double.Parse(values[0]);
double b = double.Parse(values[1]);
double c = Math.Sqrt(a * a + b * b);

byte[] response = Encoding.UTF8.GetBytes(c.ToString());
clientSocket.Send(response);
clientSocket.Close();
serverSocket.Close();