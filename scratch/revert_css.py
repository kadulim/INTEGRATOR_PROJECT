import os

files = [
    r'c:\Users\ogust\OneDrive\Desktop\INTEGRATOR_PROJECT\static\css\shared.css',
    r'c:\Users\ogust\OneDrive\Desktop\INTEGRATOR_PROJECT\static\css\dashboard.css',
    r'c:\Users\ogust\OneDrive\Desktop\INTEGRATOR_PROJECT\static\css\equipes.css',
    r'c:\Users\ogust\OneDrive\Desktop\INTEGRATOR_PROJECT\static\css\projetos.css',
    r'c:\Users\ogust\OneDrive\Desktop\INTEGRATOR_PROJECT\static\css\configuracoes.css',
    r'c:\Users\ogust\OneDrive\Desktop\INTEGRATOR_PROJECT\static\css\cliente-dashboard.css',
    r'c:\Users\ogust\OneDrive\Desktop\INTEGRATOR_PROJECT\static\css\projeto-detalhe.css'
]

for file_path in files:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the first occurrence of the responsive block or any duplicates
        # We want to keep everything before the first '/* ── Responsive ── */'
        if '/* ── Responsive ── */' in content:
            new_content = content.split('/* ── Responsive ── */')[0].strip()
            # Also handle the accidental duplications by checking if the start of the file repeats
            # This is a bit tricky, but usually the first few lines are unique.
            
            # For now, let's just truncate at the first responsive block.
            # And then we might need to manually check for the duplications I caused.
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content + '\n')
            print(f'Truncated {file_path}')
        else:
            print(f'No responsive block in {file_path}')
