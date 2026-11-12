import PyInstaller.__main__
import os
import shutil

# Очистка старых файлов сборки
print("Очистка старых файлов сборки...")
folders_to_remove = ['build', 'dist']
files_to_remove = ['Core Graph.spec']

for folder in folders_to_remove:
    if os.path.exists(folder):
        shutil.rmtree(folder)
        print(f"  Удалена папка: {folder}")

for file in files_to_remove:
    if os.path.exists(file):
        os.remove(file)
        print(f"  Удален файл: {file}")

# Параметры сборки
args = [
    'main.py',                      
    '--onefile',                    
    '--name=Core Graph',            
    '--add-binary=CoreGraph.dll;.',
    '--add-data=Assets;Assets',
    '--clean',                      
    '--noconsole',               
    '--icon=C:\\Users\\User\\Downloads\\graph_icon.ico'        
]

print("Начинается сборка")
PyInstaller.__main__.run(args)
print("Сборка завершена!")
























