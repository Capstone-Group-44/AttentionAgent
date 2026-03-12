import platform
import subprocess
import sys

class NotificationService:
    """
    A modular service to handle OS-native notifications.
    Supports macOS and Windows natively without heavy external libraries.
    """
    
    @staticmethod
    def send_notification(title: str, message: str, sound: bool = True):
        current_os = platform.system()
        
        if current_os == "Darwin":
            NotificationService._send_mac_notification(title, message, sound)
        elif current_os == "Windows":
            NotificationService._send_windows_notification(title, message, sound)
        else:
            print(f"Notifications not supported natively on {current_os}")

    @staticmethod
    def _send_mac_notification(title: str, message: str, sound: bool):
        # Using AppleScript to send a native macOS notification
        script = f'display notification "{message}" with title "{title}"'
        if sound:
            script += ' sound name "Ping"'
            
        try:
            subprocess.run(["osascript", "-e", script], check=True)
        except Exception as e:
            print(f"Failed to send macOS notification: {e}")

    @staticmethod
    def _send_windows_notification(title: str, message: str, sound: bool):
        # Using PowerShell to send a native Windows Toast notification
        ps_script = f"""
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
        [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
        $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
        $toastXml = [xml]$template.GetXml()
        $toastXml.GetElementsByTagName("text")[0].AppendChild($toastXml.CreateTextNode("{title}")) > $null
        $toastXml.GetElementsByTagName("text")[1].AppendChild($toastXml.CreateTextNode("{message}")) > $null
        """
        
        if sound:
            ps_script += """
        $audio = $toastXml.CreateElement("audio")
        $audio.SetAttribute("src", "ms-winsoundevent:Notification.Default")
        $toastXml.selectSingleNode("/toast").AppendChild($audio) > $null
        """
        else:
            ps_script += """
        $audio = $toastXml.CreateElement("audio")
        $audio.SetAttribute("silent", "true")
        $toastXml.selectSingleNode("/toast").AppendChild($audio) > $null
        """
            
        ps_script += """
        $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
        $xml.LoadXml($toastXml.OuterXml)
        $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Screen Gaze").Show($toast)
        """
        
        try:
            kwargs = {}
            if sys.platform == 'win32':
                kwargs['creationflags'] = 0x08000000  # CREATE_NO_WINDOW
            subprocess.run(["powershell", "-Command", ps_script], check=True, **kwargs)
        except Exception as e:
            print(f"Failed to send Windows notification: {e}")
