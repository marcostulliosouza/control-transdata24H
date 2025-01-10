# setup.py
from cx_Freeze import setup, Executable
import os

# Lista de módulos que você está usando no seu script
modules = ["csv", "configparser", "os", "datetime", "tkinter"]

# Inclua automaticamente todos os pacotes necessários
packages = ["encodings"]

# Se o seu aplicativo usa arquivos adicionais, especifique-os aqui
# Especifica os arquivos que precisam ser incluídos no pacote final
include_files = [
    "config.ini",                # Inclui o arquivo config.ini
    "state.json",
    "img",                        # Inclui a pasta img
    "logs"                        # Inclui a pasta logs
]

# Configuração do executável
executables = [Executable("main.py", base="Win32GUI")]

setup(
    name="Controle de Testes Transdata24H",
    version="2.0",
    options={
        "build_exe": {
            "packages": modules + packages,
            "include_files": include_files,
            "include_msvcr": True,
        }
    },
    executables=executables
)
