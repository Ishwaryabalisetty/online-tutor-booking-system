import re 
content = open('app.py', 'r').read() 
content = content.replace("app.run(debug=True)", "app.run(host='0.0.0.0', port=int(__import__('os').environ.get('PORT', 5000)), debug=False)") 
open('app.py', 'w').write(content) 
