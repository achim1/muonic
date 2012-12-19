try:
   from muonic.analysis.fit import main
except ImportError:
   import os.path
   muonic_path = os.path.abspath('../../muonic')
   if not os.path.exists(muonic_path):
       raise ImportError("Make sure muonic is properly installed or set your PYTHONPATH or add a .pth file")
   else:
       import sys
       sys.path.append(muonic_path)   
       from muonic.analysis.fit import main

main()

