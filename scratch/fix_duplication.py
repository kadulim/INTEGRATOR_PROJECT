import os

files = [
    r'c:\Users\ogust\OneDrive\Desktop\INTEGRATOR_PROJECT\static\css\dashboard.css',
    r'c:\Users\ogust\OneDrive\Desktop\INTEGRATOR_PROJECT\static\css\equipes.css',
    r'c:\Users\ogust\OneDrive\Desktop\INTEGRATOR_PROJECT\static\css\projetos.css'
]

for file_path in files:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Simple duplication check: if the file contains the first line again in the middle
        if len(lines) > 0:
            first_line = lines[0]
            for i in range(1, len(lines)):
                if lines[i] == first_line:
                    # Found a potential duplication point
                    # Check if the next few lines also match
                    match = True
                    for j in range(min(10, len(lines) - i)):
                        if lines[i+j] != lines[j]:
                            match = False
                            break
                    if match:
                        print(f'Found duplication in {file_path} at line {i+1}')
                        new_lines = lines[:i]
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.writelines(new_lines)
                        print(f'Fixed {file_path}')
                        break
