package main.java.com.cloudstorage;

public class Main {
    public static void main(String[] args) {
        CloudServer server = new CloudServer();
        new CloudGui(server); // Launch GUI
    }
}