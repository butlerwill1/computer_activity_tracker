from setuptools import setup

APP = ['src/main.py']  # Your main script
OPTIONS = {
    'argv_emulation': True,  # Allows your app to open with double-click
    'includes': ['activity_tracker_class', 'ctypes'],  # Include your custom modules and ctypes
    'iconfile': 'keyboard_mouse.icns',  # Optional: add a .icns icon file
    'frameworks': ['/usr/local/opt/libffi/lib/libffi.8.dylib'],  # Ensure libffi is bundled
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
