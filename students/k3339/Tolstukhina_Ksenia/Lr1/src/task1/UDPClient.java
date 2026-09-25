package task1;

import java.net.*;

public class UDPClient {
  public static void main(String[] args) throws Exception {
    String HOST = "localhost";
    int PORT = 8080;

    DatagramSocket socket = new DatagramSocket();
    InetAddress serverAddress = InetAddress.getByName(HOST);

    String request = "Hello, server";
    byte[] encodedRequest = request.getBytes("UTF-8");
    DatagramPacket requestPacket = new DatagramPacket(encodedRequest, encodedRequest.length, serverAddress, PORT);
    socket.send(requestPacket);

    byte[] buffer = new byte[1024];
    DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
    socket.receive(packet);
    String serverMsg = new String(packet.getData(), 0, packet.getLength(), "UTF-8");
    System.out.println("Server message: " + serverMsg);

    socket.close();
  }
}