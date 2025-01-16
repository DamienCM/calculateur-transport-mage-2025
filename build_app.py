# build_app.py
import PyInstaller.__main__
import shutil
import os
from pathlib import Path
import subprocess

def build_windows_app():
    # Clean previous builds
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("installation_package"):
        shutil.rmtree("installation_package")
    
    # Project structure
    project_root = Path(".")
    src_dir = project_root / "src"
    data_dir = project_root / "data"
    icons_dir = project_root / "icons"
    
    # Application name (with spaces)
    APP_NAME = "Calculateur Transports"
    
    # Define icon path
    icon_path = str(icons_dir / "Logo-MAGE-Application.ico")  # Update with your actual icon name
    
    # Collect all source files
    src_files = list(src_dir.rglob("*.py"))
    if not src_files:
        raise FileNotFoundError("No Python source files found in src directory")
    
    # Identify main script (assuming it's in src directory)
    main_script = str("src/__main__.py")  # Update this to point to your actual main script
    
    # PyInstaller command line arguments
    args = [
        main_script,
        f'--name={APP_NAME}',
        '--onedir',  # Changed from onefile to onedir
        # '--noconsole',
        '--clean',
        f'--icon={icon_path}' if os.path.exists(icon_path) else None,
        f'--paths={src_dir}',
        '--add-binary=%s;.' % str(src_dir),
        '--hidden-import=numpy',
        '--hidden-import=pandas'
    ]
    
    # Remove None values
    args = [arg for arg in args if arg is not None]
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    # After PyInstaller completes, sign the executable
    dist_path = Path('dist') / APP_NAME / f'{APP_NAME}.exe'
    if dist_path.exists():
        sign_command = [
            'signtool', 'sign',
            '/fd', 'SHA256',
            '/f', 'certificate.pfx',
            '/p', 'MAGE2025',
            str(dist_path)
        ]
        try:
            subprocess.run(sign_command, check=True)
            print(f"Successfully signed {dist_path}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to sign executable: {e}")


    # Create installation folder structure
    install_dir = Path("installation_package")
    install_dir.mkdir(exist_ok=True)
    
    # Copy the entire dist directory content
    app_dir = Path("dist") / APP_NAME
    if app_dir.exists():
        shutil.copytree(app_dir, install_dir / APP_NAME / "bin", dirs_exist_ok=True)
    else:
        raise FileNotFoundError(f"Build directory not found: {app_dir}")
    
    # Copy project folders
    if data_dir.exists():
        shutil.copytree(data_dir, install_dir / APP_NAME / "data", dirs_exist_ok=True)
    if icons_dir.exists():
        shutil.copytree(icons_dir, install_dir / APP_NAME / "icons", dirs_exist_ok=True)
    # os.mkdir(install_dir / APP_NAME / "bin/bin/")
    # shutil.copy2(src_dir/"bin/partition_optimizer.c", install_dir / APP_NAME / "bin/bin/partition_optimizer.c")
    # shutil.copy2(src_dir/"bin/libpartition_optimizer.so", install_dir / APP_NAME / "bin/bin/libpartition_optimizer.so")
    
    # Create README
    readme_content = """
    Calculateur Transports - Instructions d'installation
    
    1. Extrayez tout le contenu de ce fichier ZIP dans un dossier de votre choix
    2. Ouvrez le dossier "Calculateur Transports" Puis "bin"
    3. Double-cliquez sur "Calculateur Transports.exe" pour démarrer l'application
    4. Un raccourci peut etre creee
    5. Pour le support, contactez : d.cartier-millon@mage-application.com
    

    Note : Ne déplacez ni ne supprimez aucun des fichiers ou dossiers - ils sont tous nécessaires au bon fonctionnement de l'application.
    Note2 : Sous data il y a des csv qui gerent les tarifs et autres donnees d'entree. On peut modifier mais avec precaution
    """
    
    with open(install_dir / "README.txt", "w", encoding='utf-8') as f:
        f.write(readme_content)
    
    # Create ZIP file
    zip_name = "Calculateur_Transports_Installation"
    if os.path.exists(f"{zip_name}.zip"):
        os.remove(f"{zip_name}.zip")
    shutil.make_archive(zip_name, "zip", install_dir)
    
    print("Build completed successfully!")
    print(f"Installation package created: {os.path.abspath(f'{zip_name}.zip')}")

if __name__ == "__main__":
    build_windows_app()