import PyInstaller.__main__
import os

def build():
    # Define the main script
    main_script = 'main.py'
    
    # Define the output name
    exe_name = 'EmailAgent'
    
    # PyInstaller arguments
    args = [
        main_script,
        '--onefile',
        '--noconsole',
        '--name', exe_name,
        '--clean',
        '--add-data', 'VERSION.txt;.',
        # Add any hidden imports if necessary
        '--hidden-import', 'schedule',
        '--hidden-import', 'imap_tools',
        '--hidden-import', 'google.generativeai',
        '--hidden-import', 'dotenv',
        '--hidden-import', 'telebot',
        # If there are icons, add them here
        # '--icon', 'icon.ico',
    ]
    
    print(f"Building {exe_name}.exe...")
    PyInstaller.__main__.run(args)
    print("Build complete.")

if __name__ == '__main__':
    build()
