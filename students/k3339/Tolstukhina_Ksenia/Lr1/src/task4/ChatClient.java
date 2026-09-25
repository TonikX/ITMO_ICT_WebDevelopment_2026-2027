package task4;

import java.io.*;
import java.net.Socket;

public class ChatClient {
  public static void main(String[] args) throws IOException {
    String HOST = "localhost";
    int PORT = 8080;

    Socket socket = new Socket(HOST, PORT);
    BufferedReader input = new BufferedReader(new InputStreamReader(socket.getInputStream(), "UTF-8"));
    PrintWriter output = new PrintWriter(new OutputStreamWriter(socket.getOutputStream(), "UTF-8"), true);
    BufferedReader console = new BufferedReader(new InputStreamReader(System.in, "UTF-8"));

    System.out.println(input.readLine());
    String response;
    do {
      String nickName = console.readLine();
      output.println(nickName);
      response = input.readLine();
      if (response == null) {
        System.out.println("The server closed the connection");
        return;
      }
      if (!response.equals("OK")) System.out.println(response);
    } while (!response.equals("OK"));

    System.out.println("Connection established. To exit, enter /exit");

    Thread readerThread = new Thread(() -> {
      try {
        String message;
        while ((message = input.readLine()) != null) System.out.println(message);
      } catch (IOException e) {
        System.out.println("The connection is closed");
      }
    });
    readerThread.setDaemon(true);
    readerThread.start();

    String userInput;
    while ((userInput = console.readLine()) != null) {
      if (userInput.trim().isEmpty()) continue;
      output.println(userInput);
      if (userInput.equalsIgnoreCase("/exit")) break;
    }
    System.out.println("You have left the chat");
    socket.close();
  }
}
