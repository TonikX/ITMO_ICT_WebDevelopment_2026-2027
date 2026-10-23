package task1;

import java.net.*;

public class UDPServer {
  public static void main(String[] args) throws Exception {
    int PORT = 8080;

    DatagramSocket socket = new DatagramSocket(PORT);
    System.out.println("The server is running on port 8080...");
    byte[] buffer = new byte[1024];

    DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
    socket.receive(packet);
    String clientMsg = new String(packet.getData(), 0, packet.getLength(), "UTF-8");
    System.out.println("Client message: " + clientMsg);

    String response = "Hello, client";
    byte[] encodedResponse = response.getBytes("UTF-8");
    DatagramPacket responsePacket = new DatagramPacket(encodedResponse, encodedResponse.length, packet.getAddress(), packet.getPort());
    socket.send(responsePacket);

    socket.close();
  }
}