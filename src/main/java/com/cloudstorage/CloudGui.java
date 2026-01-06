package main.java.com.cloudstorage;

import javax.swing.*;
import java.awt.*;

public class CloudGui extends JFrame {

    private CloudServer server;
    private JTextField username;
    private JPasswordField password;

    public CloudGui(CloudServer server) {
        this.server = server;

        setTitle("Cloud Storage Login");
        setSize(400, 200);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);

        buildUI();
        setVisible(true);
    }

    private void buildUI() {
        JPanel panel = new JPanel(new GridLayout(3, 2, 5, 5));

        panel.add(new JLabel("Username:"));
        username = new JTextField();
        panel.add(username);

        panel.add(new JLabel("Password:"));
        password = new JPasswordField();
        panel.add(password);

        JButton login = new JButton("Login");
        JButton register = new JButton("Register");

        panel.add(login);
        panel.add(register);

        add(panel);

        login.addActionListener(e -> login());
        register.addActionListener(e -> register());
    }

    private void login() {
        User user = server.login(username.getText(),
                new String(password.getPassword()));

        if (user != null) {
            new CloudDriveGUI(user);
            dispose();
        } else {
            JOptionPane.showMessageDialog(this, "Invalid login");
        }
    }

    private void register() {
        server.registerUser(username.getText(),
                new String(password.getPassword()));
        JOptionPane.showMessageDialog(this, "User registered");
    }
}