
import os
files = [
    'app.py', 
    'requirements.txt', 
    'templates/layout.html', 
    'templates/submit.html', 
    'templates/admin.html', 
    'templates/ticket_detail.html'
]
for f in files:
    path = os.path.join('/Users/n8storm/it_helpdesk', f)
    print(f'Checking {f}: {os.path.exists(path)}')
