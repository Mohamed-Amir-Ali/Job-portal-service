package main.java.com.cloudstorage;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;

public class FileManager {

    public static String basePath = "CloudFiles";

    // Create folder for user
    public static void createUserFolder(String username) {
        File folder = new File(basePath + File.separator + username);
        if (!folder.exists())
            folder.mkdirs();
    }

    // Create subfolder
    public static void createSubFolder(String username, String folderName) {
        File folder = new File(basePath + File.separator + username + File.separator + folderName);
        if (!folder.exists())
            folder.mkdirs();
    }

    // Upload file
    public static void uploadFile(String username, String folderName, String sourcePath) throws IOException {
        File source = new File(sourcePath);
        if (!source.exists())
            throw new IOException("File does not exist");

        File targetFolder = new File(basePath + File.separator + username + File.separator + folderName);
        if (!targetFolder.exists())
            targetFolder.mkdirs();

        File target = new File(targetFolder, source.getName());
        Files.copy(source.toPath(), target.toPath(), StandardCopyOption.REPLACE_EXISTING);
    }

    // List files in folder
    public static void listFiles(String username, String folderName) {
        File folder = new File(basePath + File.separator + username + File.separator + folderName);
        if (folder.exists()) {
            File[] files = folder.listFiles();
            if (files != null && files.length > 0) {
                System.out.println("Files in " + folderName + ":");
                for (File f : files) {
                    System.out.println("- " + f.getName());
                }
            } else
                System.out.println("Folder is empty");
        } else
            System.out.println("Folder does not exist");
    }
}