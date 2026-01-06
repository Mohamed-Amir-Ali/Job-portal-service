package main.java.com.cloudstorage;

import javax.swing.*;
import javax.swing.tree.*;
import java.awt.*;
import java.awt.event.*;
import java.io.*;

public class CloudDriveGUI extends JFrame {

    private User currentUser;
    private JTree fileTree;
    private DefaultTreeModel treeModel;

    public CloudDriveGUI(User user) {
        this.currentUser = user;

        setTitle("Cloud Drive - " + user.username);
        setSize(800, 500);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);

        buildUI();
        loadTree();

        setVisible(true);
    }

    // ---------------- UI ----------------
    private void buildUI() {
        setLayout(new BorderLayout());

        DefaultMutableTreeNode root = new DefaultMutableTreeNode("Loading...");
        treeModel = new DefaultTreeModel(root);
        fileTree = new JTree(treeModel);

        add(new JScrollPane(fileTree), BorderLayout.CENTER);

        // Buttons
        JButton uploadBtn = new JButton("Upload");
        JButton openBtn = new JButton("Open");
        JButton downloadBtn = new JButton("Download");
        JButton deleteBtn = new JButton("Delete");
        JButton shareBtn = new JButton("Share");

        JPanel panel = new JPanel();
        panel.add(uploadBtn);
        panel.add(openBtn);
        panel.add(downloadBtn);
        panel.add(deleteBtn);
        panel.add(shareBtn);

        add(panel, BorderLayout.SOUTH);

        uploadBtn.addActionListener(e -> uploadFile());
        openBtn.addActionListener(e -> openFile());
        downloadBtn.addActionListener(e -> downloadFile());
        deleteBtn.addActionListener(e -> deleteFile());
        shareBtn.addActionListener(e -> shareFile());

        // Right-click menu
        JPopupMenu menu = new JPopupMenu();
        JMenuItem mOpen = new JMenuItem("Open");
        JMenuItem mDownload = new JMenuItem("Download");
        JMenuItem mDelete = new JMenuItem("Delete");

        menu.add(mOpen);
        menu.add(mDownload);
        menu.add(mDelete);

        mOpen.addActionListener(e -> openFile());
        mDownload.addActionListener(e -> downloadFile());
        mDelete.addActionListener(e -> deleteFile());

        fileTree.addMouseListener(new MouseAdapter() {
            public void mousePressed(MouseEvent e) {
                if (SwingUtilities.isRightMouseButton(e)) {
                    TreePath path = fileTree.getPathForLocation(e.getX(), e.getY());
                    if (path != null) {
                        fileTree.setSelectionPath(path);
                        menu.show(fileTree, e.getX(), e.getY());
                    }
                }
            }
        });
    }

    // ---------------- LOAD TREE ----------------
    private void loadTree() {

        DefaultMutableTreeNode root;
        File baseFolder;

        if (currentUser.role.equals("ADMIN")) {
            root = new DefaultMutableTreeNode("ALL USERS");
            baseFolder = new File(FileManager.basePath);
        } else {
            root = new DefaultMutableTreeNode(currentUser.username);
            baseFolder = new File(FileManager.basePath + File.separator + currentUser.username);
        }

        buildNodes(root, baseFolder);
        treeModel.setRoot(root);
    }

    private void buildNodes(DefaultMutableTreeNode node, File file) {
        if (file.isDirectory()) {
            File[] files = file.listFiles();
            if (files == null)
                return;

            for (File f : files) {
                DefaultMutableTreeNode child = new DefaultMutableTreeNode(f.getName());
                node.add(child);
                buildNodes(child, f);
            }
        }
    }

    // ---------------- GET SELECTED FILE ----------------
    private File getSelectedFile() {
        TreePath path = fileTree.getSelectionPath();
        if (path == null)
            return null;

        File base = currentUser.role.equals("ADMIN")
                ? new File(FileManager.basePath)
                : new File(FileManager.basePath + File.separator + currentUser.username);

        Object[] nodes = path.getPath();
        File file = base;

        for (int i = 1; i < nodes.length; i++) {
            file = new File(file, nodes[i].toString());
        }
        return file;
    }

    // ---------------- UPLOAD ----------------
    private void uploadFile() {
        JFileChooser chooser = new JFileChooser();
        if (chooser.showOpenDialog(this) == JFileChooser.APPROVE_OPTION) {
            File src = chooser.getSelectedFile();
            File dest = new File(FileManager.basePath + File.separator +
                    currentUser.username + File.separator + src.getName());
            try {
                copyFile(src, dest);
                loadTree();
            } catch (Exception e) {
                JOptionPane.showMessageDialog(this, "Upload failed");
            }
        }
    }

    // ---------------- OPEN ----------------
    private void openFile() {
        try {
            File file = getSelectedFile();
            if (file != null && file.isFile())
                Desktop.getDesktop().open(file);
        } catch (Exception e) {
            JOptionPane.showMessageDialog(this, "Cannot open file");
        }
    }

    // ---------------- DOWNLOAD ----------------
    private void downloadFile() {
        File file = getSelectedFile();
        if (file == null || !file.isFile())
            return;

        JFileChooser chooser = new JFileChooser();
        chooser.setSelectedFile(new File(file.getName()));

        if (chooser.showSaveDialog(this) == JFileChooser.APPROVE_OPTION) {
            try {
                copyFile(file, chooser.getSelectedFile());
            } catch (Exception e) {
                JOptionPane.showMessageDialog(this, "Download failed");
            }
        }
    }

    // ---------------- DELETE ----------------
    private void deleteFile() {
        File file = getSelectedFile();
        if (file == null || !file.exists())
            return;

        int confirm = JOptionPane.showConfirmDialog(this,
                "Delete file?", "Confirm", JOptionPane.YES_NO_OPTION);

        if (confirm == JOptionPane.YES_OPTION) {
            file.delete();
            loadTree();
        }
    }

    // ---------------- SHARE ----------------
    private void shareFile() {
        File file = getSelectedFile();
        if (file == null || !file.isFile())
            return;

        String targetUser = JOptionPane.showInputDialog(this, "Share with user:");
        if (targetUser == null || targetUser.isEmpty())
            return;

        File shared = new File(FileManager.basePath + File.separator +
                "shared" + File.separator +
                currentUser.username + "_to_" + targetUser);

        shared.mkdirs();

        try {
            copyFile(file, new File(shared, file.getName()));
            JOptionPane.showMessageDialog(this, "File shared!");
        } catch (Exception e) {
            JOptionPane.showMessageDialog(this, "Sharing failed");
        }
    }

    // ---------------- COPY ----------------
    private void copyFile(File src, File dest) throws IOException {
        try (InputStream in = new FileInputStream(src);
                OutputStream out = new FileOutputStream(dest)) {

            byte[] buffer = new byte[1024];
            int len;
            while ((len = in.read(buffer)) > 0) {
                out.write(buffer, 0, len);
            }
        }
    }
}