package main.java.com.cloudstorage;

import java.io.IOException;
import java.util.Scanner;

public class CloudClient {

    CloudServer server;
    User user;
    Scanner scanner = new Scanner(System.in);

    public CloudClient(CloudServer server) {
        this.server = server;
    }

    public void start() {
        while (true) {
            System.out.println("\n1. Register");
            System.out.println("2. Login");
            System.out.println("3. Exit");
            System.out.print("Option: ");
            int option = scanner.nextInt();
            scanner.nextLine();

            if (option == 1) {
                System.out.print("Enter username: ");
                String u = scanner.nextLine();
                System.out.print("Enter password: ");
                String p = scanner.nextLine();
                server.registerUser(u, p);
            } else if (option == 2) {
                System.out.print("Enter username: ");
                String u = scanner.nextLine();
                System.out.print("Enter password: ");
                String p = scanner.nextLine();
                user = server.login(u, p);
                if (user != null) {
                    if (user.role.equals("ADMIN"))
                        adminMenu();
                    else
                        userMenu();
                }
            } else
                break;
        }
    }

    // User menu
    public void userMenu() {
        while (true) {
            System.out.println("\n1. Create Folder");
            System.out.println("2. Upload File");
            System.out.println("3. List Files");
            System.out.println("4. Logout");
            System.out.print("Option: ");
            int option = scanner.nextInt();
            scanner.nextLine();

            try {
                if (option == 1) {
                    System.out.print("Folder name: ");
                    String folder = scanner.nextLine();
                    FileManager.createSubFolder(user.username, folder);
                    System.out.println("Folder created!");
                } else if (option == 2) {
                    System.out.print("Folder to upload to: ");
                    String folder = scanner.nextLine();
                    System.out.print("Path of file: ");
                    String path = scanner.nextLine();
                    FileManager.uploadFile(user.username, folder, path);
                    System.out.println("File uploaded!");
                } else if (option == 3) {
                    System.out.print("Folder name: ");
                    String folder = scanner.nextLine();
                    FileManager.listFiles(user.username, folder);
                } else if (option == 4)
                    break;
            } catch (IOException e) {
                System.out.println("Error: " + e.getMessage());
            }
        }
    }

    // Admin menu
    public void adminMenu() {
        while (true) {
            System.out.println("\n=== Admin Menu ===");
            System.out.println("1. List all users");
            System.out.println("2. Delete user");
            System.out.println("3. Logout");
            System.out.print("Option: ");
            int option = scanner.nextInt();
            scanner.nextLine();

            if (option == 1) {
                server.loadUsers();
            } else if (option == 2) {
                System.out.print("Enter username to delete: ");
                String username = scanner.nextLine();
                server.deleteUser(username);
            } else if (option == 3)
                break;
        }
    }
}