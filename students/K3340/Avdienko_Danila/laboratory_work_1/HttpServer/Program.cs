using System.Net;
using System.Net.Sockets;
using System.Text;

Socket serverSocket = new Socket(
    AddressFamily.InterNetwork,
    SocketType.Stream,
    ProtocolType.Tcp
);

IPEndPoint serverEndPoint = new IPEndPoint(IPAddress.Loopback, 8070);
serverSocket.Bind(serverEndPoint);
serverSocket.Listen(1);

Console.WriteLine("HTTP сервер запущен на http://127.0.0.1:8070");
Console.WriteLine("Ожидание запроса...");

Socket clientSocket = serverSocket.Accept();
byte[] requestBuffer = new byte[1024]; 
int receivedBytes = clientSocket.Receive(requestBuffer);

string request = Encoding.UTF8.GetString(requestBuffer, 0, receivedBytes);
Console.WriteLine($"Получен HTTP-запрос:\n{request}");

string html = File.ReadAllText("index.html");
byte[] htmlBytes = Encoding.UTF8.GetBytes(html);
string headers =
    "HTTP/1.1 200 OK\r\n" +
    "Content-Type: text/html; charset=UTF-8\r\n" +
    $"Content-Length: {htmlBytes.Length}\r\n" +
    "Connection: close\r\n" +
    "\r\n";

byte[] response = Encoding.UTF8.GetBytes(headers + html);
clientSocket.Send(response);

clientSocket.Close();
serverSocket.Close();