# import subprocess

# def send_notification(title, message):
#     """Displays a macOS notification using terminal-notifier."""
#     subprocess.run(["terminal-notifier", "-title", title, "-message", message])

# # Example usage
# send_notification("Test Notification", "Did this work?")


# import subprocess

# def send_alert(title, message):
#     """Displays a macOS alert dialog instead of a notification."""
#     script = f'display alert "{title}" message "{message}"'
#     subprocess.run(["osascript", "-e", script])

# # Example usage
# send_alert("Test Alert", "Did this show up?")


import subprocess

def send_notification(title, message):
    """Displays a macOS notification with sound using terminal-notifier."""
    # subprocess.run(["terminal-notifier", "-title", title, "-message", message, "-sound", "default"])
    # We can add others in here
    pass

# send_notification("Test", "Did this make a sound?")
