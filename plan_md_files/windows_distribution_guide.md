# Screen Gaze: Windows Installation & Distribution Guide

The Windows build of Screen Gaze is a "one-folder" distribution. This means all the necessary files, including the executable and its dependencies, are contained within a single directory.

## 1. Locating the Build
Your compiled application is located in the following directory:
`desktop-app\dist\ScreenGaze\`

## 2. How to "Install"
To "install" the app on your machine or another Windows PC:
1.  **Copy the Folder**: Copy the entire `ScreenGaze` folder from the `dist` directory to your desired installation location (e.g., `C:\Program Files\ScreenGaze` or your Desktop).
    > [!IMPORTANT]
    > Do NOT just copy the `ScreenGaze.exe` file. It requires the `_internal` folder and other files in its directory to run.

2.  **Create a Shortcut**:
    -   Right-click on `ScreenGaze.exe`.
    -   Select **Send to** > **Desktop (create shortcut)**.
    -   You can now launch the app from your Desktop.

## 3. Running the App
-   Double-click `ScreenGaze.exe` (or your shortcut).
-   The app will run without a console window (as configured in the build).
-   **Data Persistence**: The app stores its database and settings in your `%APPDATA%\ScreenGaze` folder. This ensures your data persists even if you update the app folder.

## 4. Distribution (Sharing with others)
To share the app with other users:
1.  Right-click the `ScreenGaze` folder in `dist`.
2.  Select **Compress to ZIP file**.
3.  Send the resulting `.zip` file to others. They just need to extract it and run the `.exe`.

## 5. Future Improvement: Professional Installer
If you want a single file installer (like a `.exe` setup or `.msi`), I recommend using **Inno Setup** (free) to package the `dist\ScreenGaze` folder.
