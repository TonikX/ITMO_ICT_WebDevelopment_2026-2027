package task5;

import java.io.*;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.*;

public class WebServer {
  private static final int PORT = 8080;
  private static final Map<String, List<Integer>> journal = new LinkedHashMap<String, List<Integer>>();

  public static void main(String[] args) throws IOException {
    ServerSocket serverSocket = new ServerSocket(PORT);
    try {
      System.out.println("The server is running on http://localhost:8080");
      while (true) {
        Socket clientSocket = serverSocket.accept();
        handleClient(clientSocket);
      }
    } finally {
      serverSocket.close();
    }
  }

  private static void handleClient(Socket clientSocket) {
    try {
      BufferedReader input = new BufferedReader(new InputStreamReader(clientSocket.getInputStream(), StandardCharsets.UTF_8));

      String requestLine = input.readLine();
      System.out.println("Запрос: " + requestLine);

      String[] parts = requestLine.split(" ");
      String method = parts[0];
      String path = parts[1];

      int contentLength = 0;
      String line;
      while (!(line = input.readLine()).isEmpty()) {
        if (line.toLowerCase().startsWith("content-length:")) {
          contentLength = Integer.parseInt(line.split(":")[1].trim());
        }
      }

      String body = "";
      if (contentLength > 0) {
        char[] buf = new char[contentLength];
        input.read(buf, 0, contentLength);
        body = new String(buf);
      }

      byte[] response;
      if (method.equals("GET")) response = handleGet(path);
      else if (method.equals("POST")) response = handlePost(path, body);
      else response = httpResponse(405, "Method Not Allowed", "<h1>405 Method Not Allowed</h1>");

      OutputStream output = clientSocket.getOutputStream();
      output.write(response);
      output.flush();
    } catch (IOException e) {
      System.out.println(e.getMessage());
    } finally {
      try { clientSocket.close(); } catch (IOException ignored) {}
    }
  }

  private static byte[] handleGet(String path) {
    if (path.equals("/")) return httpResponse(200, "OK", buildHtml());
    return httpResponse(404, "Not Found", "<h1>404 Not Found</h1>");
  }

  private static byte[] handlePost(String path, String body) {
    if (!path.equals("/")) return httpResponse(404, "Not Found", "<h1>404 Not Found</h1>");

    Map<String, String> params = parseFormBody(body);
    String discipline = params.getOrDefault("discipline", "").trim();
    String gradeStr = params.getOrDefault("grade", "").trim();

    if (discipline.isEmpty() || gradeStr.isEmpty()) return httpResponse(400, "Bad Request", "<h1>Нужно указать дисциплину и оценку</h1>");

    int grade;
    try {
      grade = Integer.parseInt(gradeStr);
    } catch (NumberFormatException e) {
      return httpResponse(400, "Bad Request", "<h1>Оценка должна быть числом</h1>");
    }

    journal.computeIfAbsent(discipline, k -> new ArrayList<>()).add(grade);

    return httpResponse(200, "OK", buildHtml());
  }

  private static Map<String, String> parseFormBody(String body) {
    Map<String, String> params = new HashMap<String, String>();
    String[] pairs = body.split("&");
    for (int i = 0; i < pairs.length; i++) {
      String pair = pairs[i];
      if (pair.isEmpty()) continue;
      String[] kv = pair.split("=", 2);
      try {
        String key = URLDecoder.decode(kv[0], "UTF-8");
        String value = kv.length > 1 ? URLDecoder.decode(kv[1], "UTF-8") : "";
        params.put(key, value);
      } catch (UnsupportedEncodingException ignored) {
      } catch (IllegalArgumentException ignored) { }
    }

    return params;
  }

  private static byte[] httpResponse(int status, String statusText, String body) {
    byte[] bodyBytes = body.getBytes(StandardCharsets.UTF_8);
    String headers = "HTTP/1.1 " + status + " " + statusText + "\r\n"
      + "Content-Type: text/html; charset=utf-8\r\n"
      + "Content-Length: " + bodyBytes.length + "\r\n"
      + "Connection: close\r\n"
      + "\r\n";

    ByteArrayOutputStream output = new ByteArrayOutputStream();
    try {
      output.write(headers.getBytes(StandardCharsets.UTF_8));
      output.write(bodyBytes);
    } catch (IOException ignored) { }
    return output.toByteArray();
  }

  private static String buildHtml() {
    StringBuilder stringBuilder = new StringBuilder();
    for (Map.Entry<String, List<Integer>> entry : journal.entrySet()) {
      List<Integer> grades = entry.getValue();

      StringBuilder gradesStr = new StringBuilder();
      for (int i = 0; i < grades.size(); i++) {
        if (i > 0) gradesStr.append(", ");
        gradesStr.append(grades.get(i));
      }

      stringBuilder.append("<tr><td>")
        .append(entry.getKey())
        .append("</td><td>")
        .append(gradesStr)
        .append("</td></tr>\n");
    }

    if (stringBuilder.length() == 0) stringBuilder.append("<tr><td colspan=\"2\">Пока нет оценок</td></tr>");

    StringBuilder html = new StringBuilder();
    html.append("<!DOCTYPE html>\n")
      .append("<html lang=\"ru\">\n")
      .append("<head>\n")
      .append("    <meta charset=\"UTF-8\">\n")
      .append("    <title>Журнал оценок</title>\n")
      .append("    <style>\n")
      .append("        body { font-family: sans-serif; margin: 40px; }\n")
      .append("        table { border-collapse: collapse; width: 100%; max-width: 600px; }\n")
      .append("        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }\n")
      .append("        th { background: #f0f0f0; }\n")
      .append("        form { margin-top: 30px; }\n")
      .append("        input { padding: 6px; margin-right: 10px; }\n")
      .append("    </style>\n")
      .append("</head>\n")
      .append("<body>\n")
      .append("    <h1>Журнал оценок по дисциплинам</h1>\n")
      .append("    <table>\n")
      .append("        <tr><th>Дисциплина</th><th>Оценки</th>\n")
      .append("        ").append(stringBuilder).append("\n")
      .append("    </table>\n")
      .append("    <form method=\"POST\" action=\"/\">\n")
      .append("        <input type=\"text\" name=\"discipline\" placeholder=\"Дисциплина\" required>\n")
      .append("        <input type=\"number\" name=\"grade\" placeholder=\"Оценка\" min=\"1\" max=\"5\" required>\n")
      .append("        <button type=\"submit\">Добавить оценку</button>\n")
      .append("    </form>\n")
      .append("</body>\n")
      .append("</html>");

    return html.toString();
  }
}
