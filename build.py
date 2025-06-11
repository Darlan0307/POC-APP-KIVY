import os
import subprocess
import shutil
import sys

def build_executable():    
    print("🔨 Iniciando build do executável pode demorar um pouco...")
    
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    print(sys.platform)
    
    sep = ";" if sys.platform.startswith("win") else ":"

    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=OracleDBManager",
        f"--add-data=services{sep}services",
        f"--add-data=screens{sep}screens",
        f"--add-data=utils{sep}utils",
        f"--add-data=widgets{sep}widgets",
        "--hidden-import=uuid",
        "--hidden-import=secrets",
        "--hidden-import=cryptography.hazmat.primitives.kdf.pbkdf2",
        "--hidden-import=cryptography.x509",
        "main.py"
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build concluído com sucesso!")
        print(f"📁 Executável salvo em: dist/OracleDBManager")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro no build: {e}")
        print(f"Saída: {e.stdout}")
        print(f"Erro: {e.stderr}")
        return False

if __name__ == "__main__":
    build_executable()