package task2;

import java.io.*;
import java.net.Socket;
import java.util.Scanner;

public class TCPClient {
  public static void main(String[] args) throws IOException {
    String HOST = "localhost";
    int PORT = 8080;

    Socket socket = new Socket(HOST, PORT);

    BufferedReader input = new BufferedReader(new InputStreamReader(socket.getInputStream(), "UTF-8"));
    PrintWriter output = new PrintWriter(new OutputStreamWriter(socket.getOutputStream(), "UTF-8"), true);

    Scanner sc = new Scanner(System.in);
    System.out.println("Enter the coefficients a, b, c: ");
    double a = sc.nextDouble();
    double b = sc.nextDouble();
    double c = sc.nextDouble();

    output.println(a);
    output.println(b);
    output.println(c);

    String result = input.readLine();
    System.out.println("Root(s): " + result);

    socket.close();
  }
}