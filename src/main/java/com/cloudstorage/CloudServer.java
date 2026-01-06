package main.java.com.cloudstorage;

import java.io.*;
import java.util.ArrayList;

public class CloudServer {

    // List that holds users in memory
    private ArrayList<User> users = new ArrayList<>();

    // Path to CSV file (same level as src folder)
    private final String USER_FILE = "data/users.csv";

    // Constructor (runs when program starts)
    public CloudServer() {
        loadUsers();
    }

    public ArrayList<User> getUsers() {
        return users;

    }

    public void setUsers(ArrayList<User> users) {
        this.users = users;

    }

    // -------------------------------
    // LOAD USERS FROM CSV FILE
    // -------------------------------
    void loadUsers() {
        File file = new File(USER_FILE);

        try {
            // Create data folder and file if not exist
            if (!file.exists()) {
                file.getParentFile().mkdirs();
                file.createNewFile();

                // Create default admin
                getUsers().add(new User("admin", "admin123", "ADMIN"));
                FileManager.createUserFolder("admin");
                saveUsers();
                return;
            }

            BufferedReader reader = new BufferedReader(new FileReader(file));
            String line;

            while ((line = reader.readLine()) != null) {
                String[] data = line.split(",");
                if (data.length == 3) {
                    getUsers().add(new User(data[0], data[1], data[2]));
                    FileManager.createUserFolder(data[0]);
                }
            }
            reader.close();

        } catch (IOException e) {
            System.out.println("Error loading users: " + e.getMessage());
        }
    }

    // -------------------------------
    // SAVE USERS TO CSV FILE
    // -------------------------------
    private void saveUsers() {
        try {
            BufferedWriter writer = new BufferedWriter(new FileWriter(USER_FILE));
            for (User user : getUsers()) {
                writer.write(user.username + "," + user.password + "," + user.role);
                writer.newLine();
            }
            writer.close();
        } catch (IOException e) {
            System.out.println("Error saving users: " + e.getMessage());
        }
    }

    // -------------------------------
    // REGISTER USER
    // -------------------------------
    public void registerUser(String username, String password) {
        getUsers().add(new User(username, password, "USER"));
        FileManager.createUserFolder(username);
        saveUsers();
    }

    // -------------------------------
    // LOGIN USER
    // -------------------------------
    public User login(String username, String password) {
        for (User user : getUsers()) {
            if (user.username.equals(username) && user.password.equals(password)) {
                return user;
            }
        }
        return null;
    }

    // -------------------------------
    // ADMIN: DELETE USER
    // -------------------------------
    public void deleteUser(String username) {
        User target = null;

        for (User user : getUsers()) {
            if (user.username.equals(username) && !user.role.equals("ADMIN")) {
                target = user;
                break;
            }
        }

        if (target != null) {
            getUsers().remove(target);
            deleteFolder(new File(FileManager.basePath + File.separator + username));
            saveUsers();
        }
    }

    // -------------------------------
    // DELETE USER FOLDER RECURSIVELY
    // -------------------------------
    private void deleteFolder(File folder) {
        if (folder.exists()) {
            for (File file : folder.listFiles()) {
                if (file.isDirectory()) {
                    deleteFolder(file);
                } else {
                    file.delete();
                }
            }
            folder.delete();
        }
    }
}