import sys
import os
sys.path.insert(0, r'C:\Users\conta\OneDrive\Desktop\project-backup\rag-api')
os.chdir(r'C:\Users\conta\OneDrive\Desktop\project-backup\rag-api')
import uvicorn
uvicorn.run('app:app', host='127.0.0.1', port=8080, log_level='info')
