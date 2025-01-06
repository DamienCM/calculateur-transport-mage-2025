# build_app.py
import PyInstaller.__main__
import shutil
import os
from pathlib import Path

def build_windows_app():
    # Ensure the dist directory is clean
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # Project structure
    project_root = Path(".")
    src_dir = project_root / "src"
    data_dir = project_root / "data"
    icons_dir = project_root / "icons"
    
    # Define icon path - assuming you have an .ico file in icons directory
    icon_path = str(icons_dir / "Logo-MAGE-Application.ico")  # Update with your actual icon name
    
    # Collect all source files
    src_files = list(src_dir.rglob("*.py"))
    if not src_files:
        raise FileNotFoundError("No Python source files found in src directory")
    
    # Identify main script (assuming it's in src directory)
    main_script = str(src_files[0])  # Update this to point to your actual main script
    
    # Define data files to include
    datas = [
        # Include all CSV files from data directory
        (str(data_dir), "data"),
        # Include icons
        (str(icons_dir), "icons"),
        # Include any other source files that might be needed for compilation
        (str(src_dir), "src")
    ]
    
    # Convert to PyInstaller format
    data_args = [f"--add-data={src};{dst}" for src, dst in datas]
    
    # Add hidden imports for any modules that might be dynamically imported
    hidden_imports = [
        '--hidden-import=numpy',  # Add any other required imports
        '--hidden-import=pandas'
    ]
    
    # PyInstaller command line arguments
    args = [
        main_script,
        '--name=Calculateur Transports',  # Replace with your app name
        '--onefile',  # Create a single executable
        # '--noconsole',  # Don't show console window
        '--clean',  # Clean cache
        f'--icon={icon_path}' if os.path.exists(icon_path) else None,
        # Add the compiled library directory to PATH
        f'--paths={src_dir}',
        # Force inclusion of binary dependencies
        '--add-binary=%s;.' % str(src_dir),
        *data_args,
        *hidden_imports
    ]
    
    # Remove None values
    args = [arg for arg in args if arg is not None]
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    # Create installation folder
    install_dir = Path("installation_package")
    install_dir.mkdir(exist_ok=True)
    
    # Move executable and create structure
    shutil.move(f"dist/Calculateur Transports.exe", install_dir / "Calculateur Transports.exe")
    
    # Create a basic README
    readme_content = """
    Application Installation Instructions
    
    1. Double click YourAppName.exe to start the application
    2. All required data files are included in the package
    3. For support, contact: your@email.com
    
    Note: The first run might take a few moments as the application initializes.
    """
    
    with open(install_dir / "README.txt", "w") as f:
        f.write(readme_content)
    
    # Create ZIP file
    shutil.make_archive("Calculateur Transports Installer", "zip", install_dir)
    
    print("Build completed successfully!")

if __name__ == "__main__":
    build_windows_app()