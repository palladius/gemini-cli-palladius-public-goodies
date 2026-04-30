
import xml.etree.ElementTree as ET
import os
import subprocess
import sys

def get_monitors():
    path = os.path.expanduser('~/.config/monitors.xml')
    if not os.path.exists(path):
        print(f"Error: {path} not found.")
        return []
    
    try:
        tree = ET.parse(path)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing {path}: {e}")
        return []
    
    monitors = []
    # Use the first configuration found
    config = root.find('configuration')
    if config is None:
        return []

    for logical in config.findall('logicalmonitor'):
        x = int(logical.find('x').text)
        y = int(logical.find('y').text)
        scale = float(logical.find('scale').text)
        
        monitor_node = logical.find('monitor')
        spec = monitor_node.find('monitorspec')
        connector = spec.find('connector').text
        product = spec.find('product').text
        
        mode = monitor_node.find('mode')
        width = int(mode.find('width').text)
        height = int(mode.find('height').text)
        
        transform = logical.find('transform')
        rotation = transform.find('rotation').text if transform is not None else 'normal'
        
        # Calculate logical bounds
        if rotation in ['left', 'right']:
            logical_width = height / scale
            logical_height = width / scale
        else:
            logical_width = width / scale
            logical_height = height / scale
            
        monitors.append({
            'connector': connector,
            'product': product,
            'x': x, 'y': y,
            'w': int(logical_width), 'h': int(logical_height),
            'rotation': rotation,
            'scale': scale
        })
    
    # Sort by X coordinate (left to right)
    monitors.sort(key=lambda m: m['x'])
    return monitors

def main():
    monitors = get_monitors()
    if not monitors:
        print("No monitors detected.")
        return

    print("Detected Monitors:")
    for i, m in enumerate(monitors):
        pos = "Left" if i == 0 else "Right" if i == len(monitors)-1 else f"Monitor {i}"
        
        # Determine emoji based on orientation
        if m['w'] > m['h']:
            orientation_emoji = "🖥️  [▭ Horizontal]"
        else:
            orientation_emoji = "📱 [▯ Vertical]"
            
        print(f"{orientation_emoji} {pos}: {m['product']} ({m['connector']}) - {m['w']}x{m['h']} at +{m['x']}+{m['y']} (Scale: {m['scale']})")

    # Target the left monitor
    left = monitors[0]
    output_dir = "tmp-screenshots"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, "left_monitor.png")
    
    print(f"\nTargeting Left Monitor: {left['w']}x{left['h']}+{left['x']}+{left['y']}")
    
    # Attempt to take a screenshot using gnome-screenshot (might require session interaction)
    # Since Wayland is tricky, we suggest taking a full screenshot and cropping if this fails.
    print(f"Attempting to capture screenshot to {output_file}...")
    
    # We use a full capture first because gnome-screenshot -a is interactive
    # and coordinates are often ignored in Wayland CLI.
    try:
        # Note: In some Wayland setups, gnome-screenshot -f works if run within the session.
        # If it fails, we provide the manual crop command.
        subprocess.run(["gnome-screenshot", "-f", "/tmp/full_capture.png"], check=False)
        
        if os.path.exists("/tmp/full_capture.png"):
            # Crop to the left monitor bounds
            # convert /tmp/full_capture.png -crop WxH+X+Y output.png
            crop_cmd = [
                "convert", "/tmp/full_capture.png", 
                "-crop", f"{left['w']}x{left['h']}+{left['x']}+{left['y']}",
                output_file
            ]
            subprocess.run(crop_cmd, check=True)
            print(f"Success! Screenshot saved to {output_file}")
        else:
            print("Automatic capture failed (likely Wayland permissions).")
            print(f"Please take a full screenshot manually and save it as /tmp/full_capture.png, then run this script again.")
            print(f"Or use this crop command: convert full_screenshot.png -crop {left['w']}x{left['h']}+{left['x']}+{left['y']} {output_file}")
            
    except Exception as e:
        print(f"Error during capture/crop: {e}")

if __name__ == "__main__":
    main()
