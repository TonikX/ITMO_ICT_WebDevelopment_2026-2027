package task2;

import java.io.*;
import java.net.ServerSocket;
import java.net.Socket;

public class TCPServer {
  public static void main(String[] args) throws IOException {
    int PORT = 8080;

    ServerSocket socket = new ServerSocket(PORT);
    System.out.println("The server is running on port 8080...");

    Socket clientSocket = socket.accept();
    System.out.println("The client has connected");

    BufferedReader input = new BufferedReader(new InputStreamReader(clientSocket.getInputStream(), "UTF-8"));
    PrintWriter output = new PrintWriter(new OutputStreamWriter(clientSocket.getOutputStream(), "UTF-8"), true);

    double a = Double.parseDouble(input.readLine());
    double b = Double.parseDouble(input.readLine());
    double c = Double.parseDouble(input.readLine());

    double discriminant = b * b - 4 * a * c;
    if (discriminant > 0){
      double x1 = (-b + Math.sqrt(discriminant)) / (2 * a);
      double x2 = (-b - Math.sqrt(discriminant)) / (2 * a);
      output.println(x1 + " " + x2);
    } else if (discriminant == 0) {
      double x = -b / (2 * a);
      output.println(x);
    } else {
      output.println("no roots");
    }
    System.out.println("The response has been sent");
    clientSocket.close();
    socket.close();
  }
}
