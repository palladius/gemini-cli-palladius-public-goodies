import sys
import os
import urllib.request
from gi.repository import GLib, Gio

loop = GLib.MainLoop()
output_file = os.path.abspath("tmp-screenshots/portal_screenshot.png")

def on_response(connection, sender_name, object_path, interface_name, signal_name, parameters, user_data):
    response, results = parameters.unpack()
    if response == 0:
        uri = results.get("uri")
        if uri:
            print(f"Success! Screenshot saved by portal at: {uri}")
            
            # The portal saves it in a temporary location, let's copy it to our folder
            try:
                # Convert file:// uri to local path and copy
                req = urllib.request.urlopen(uri)
                with open(output_file, 'wb') as f:
                    f.write(req.read())
                print(f"Copied to: {output_file}")
            except Exception as e:
                print(f"Error copying file: {e}")
        else:
            print("Success, but no URI was returned.")
    elif response == 1:
        print("Screenshot request was cancelled by the user.")
    else:
        print(f"Screenshot failed or was denied. Response code: {response}")
    loop.quit()

def main():
    bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)

    request_token = "gemini_screenshot"
    sender = bus.get_unique_name()[1:].replace('.', '_')
    request_path = f"/org/freedesktop/portal/desktop/request/{sender}/{request_token}"

    bus.signal_subscribe(
        "org.freedesktop.portal.Desktop",
        "org.freedesktop.portal.Request",
        "Response",
        request_path,
        None,
        Gio.DBusSignalFlags.NONE,
        on_response,
        None
    )

    print("Please check your screen for a screenshot permission dialog...")
    
    options_dict = {
        "handle_token": GLib.Variant("s", request_token),
        "interactive": GLib.Variant("b", True)
    }

    bus.call(
        "org.freedesktop.portal.Desktop",
        "/org/freedesktop/portal/desktop",
        "org.freedesktop.portal.Screenshot",
        "Screenshot",
        GLib.Variant("(sa{sv})", ("", options_dict)),
        None,
        Gio.DBusCallFlags.NONE,
        -1,
        None
    )

    # Run the event loop to wait for the signal
    try:
        loop.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        loop.quit()

if __name__ == "__main__":
    main()
