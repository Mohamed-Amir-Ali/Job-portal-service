package main.java.com.cloudstorage;

import javax.swing.*;
import java.awt.*;

public class AdminGUI extends JFrame {

    CloudServer server;
    DefaultListModel<String> userListModel = new DefaultListModel<>();
    JList<String> userList = new JList<>(userListModel);

    public AdminGUI(CloudServer server) {
        this.server = server;
        setTitle("Admin Panel");
        setSize(400, 300);
        setLocationRelativeTo(null);
        setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);

        JButton refreshButton = new JButton("Refresh Users");
        JButton deleteButton = new JButton("Delete User");

        JPanel topPanel = new JPanel();
        topPanel.add(refreshButton);
        topPanel.add(deleteButton);

        add(topPanel, BorderLayout.NORTH);
        add(new JScrollPane(userList), BorderLayout.CENTER);

        refreshButton.addActionListener(e -> refreshUsers());
        deleteButton.addActionListener(e -> deleteUser());

        refreshUsers();
        setVisible(true);
    }

    private void refreshUsers() {
        userListModel.clear();
        for (User u : server.getUsers()) {
            userListModel.addElement(u.username + " (" + u.role + ")");
        }
    }

    private void deleteUser() {
        String selected = userList.getSelectedValue();
        if (selected != null) {
            String username = selected.split(" ")[0];
            server.deleteUser(username);
            refreshUsers();
        }
    }
}