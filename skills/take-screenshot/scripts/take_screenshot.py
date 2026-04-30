#!/usr/bin/env python3
import sys
import os
import subprocess
import argparse

def capture_mac(output_file, monitor_index=None):
    """Captures screenshot on macOS using the built-in screencapture utility."""
    print("Detected macOS. Using 'screencapture'.")
    cmd = ["screencapture", "-x"] # -x = do not play sounds
    
    if monitor_index is not None:
        # -D 1 is main display, -D 2 is secondary, etc.
        cmd.extend(["-D", str(monitor_index)])
    
    cmd.append(output_file)
    
    print(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print(f"Success! Screenshot saved to {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error capturing screenshot on Mac: {e}")
        return False

def capture_linux_portal(output_file, interactive=True):
    """Captures screenshot on Linux Wayland using the official XDG Desktop Portal.
    Requires gi module (PyGObject)."""
    if interactive:
        print("Detected Linux (likely Wayland). Using XDG Desktop Portal (secure, prompts user).")
    else:
        print("Detected Linux (likely Wayland). Using XDG Desktop Portal in NON-INTERACTIVE mode.")
    try:
        import urllib.request
        from gi.repository import GLib, Gio
    except ImportError:
        print("Error: 'gi' module not found. On Debian/Ubuntu, install 'python3-gi'.")
        return False

    loop = GLib.MainLoop()
    success = False

    def on_response(connection, sender_name, object_path, interface_name, signal_name, parameters, user_data):
        nonlocal success
        response, results = parameters.unpack()
        if response == 0:
            uri = results.get("uri")
            if uri:
                try:
                    req = urllib.request.urlopen(uri)
                    with open(output_file, 'wb') as f:
                        f.write(req.read())
                    print(f"Success! Screenshot copied to: {output_file}")
                    success = True
                except Exception as e:
                    print(f"Error copying file: {e}")
            else:
                print("Success, but no URI was returned by the portal.")
        elif response == 1:
            print("Screenshot request was cancelled by the user.")
        else:
            print(f"Screenshot failed or was denied. Response code: {response}")
        loop.quit()

    bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
    request_token = "gemini_screenshot"
    sender = bus.get_unique_name()[1:].replace('.', '_')
    request_path = f"/org/freedesktop/portal/desktop/request/{sender}/{request_token}"

    bus.signal_subscribe(
        "org.freedesktop.portal.Desktop", "org.freedesktop.portal.Request",
        "Response", request_path, None, Gio.DBusSignalFlags.NONE,
        on_response, None
    )

    if interactive:
        print(">>> Please check your screen for a screenshot permission dialog! <<<")
    else:
        print(">>> Using non-interactive screenshot mode! <<<")

    options_dict = {
        "handle_token": GLib.Variant("s", request_token),
        "interactive": GLib.Variant("b", interactive)
    }

    bus.call(
        "org.freedesktop.portal.Desktop", "/org/freedesktop/portal/desktop",
        "org.freedesktop.portal.Screenshot", "Screenshot",
        GLib.Variant("(sa{sv})", ("", options_dict)),
        None, Gio.DBusCallFlags.NONE, -1, None
    )

    try:
        loop.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        loop.quit()
        
    return success

def capture_linux_x11(output_file):
    """Fallback for Linux X11 systems using import (ImageMagick)."""
    print("Attempting fallback with 'import -window root' (X11).")
    cmd = ["import", "-window", "root", output_file]
    try:
        subprocess.run(cmd, check=True)
        print(f"Success! Screenshot saved to {output_file}")
        return True
    except subprocess.CalledProcessError:
        print("X11 fallback failed. Are you on Wayland without the XDG Portal?")
        return False
    except FileNotFoundError:
        print("Error: 'import' command not found. Install ImageMagick.")
        return False

def main():
    parser = argparse.ArgumentParser(description="Cross-platform screenshot tool for Gemini CLI")
    parser.add_argument("output", help="Path to save the screenshot")
    parser.add_argument("--mac-display", type=int, help="On macOS, specify display index (1, 2, etc.)")
    parser.add_argument("--non-interactive", action="store_true", help="Attempt to capture without prompting the user (Linux Wayland)")
    
    args = parser.parse_args()
    output_file = os.path.abspath(args.output)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
    
    platform = sys.platform
    
    if platform == "darwin":
        capture_mac(output_file, monitor_index=args.mac_display)
    elif platform.startswith("linux"):
        # Wayland is the default on modern Linux, and the portal is the only secure way.
        # It handles multi-monitor via its native UI picker.
        interactive_mode = not args.non_interactive
        if not capture_linux_portal(output_file, interactive=interactive_mode):
            # Fallback to X11 if portal fails or gi is missing
            capture_linux_x11(output_file)
    else:
        print(f"Unsupported OS: {platform}")

if __name__ == "__main__":
    main()
