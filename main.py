import logging
import sys
import os
import multiprocessing

# Configuração de Log
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app_errors.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

from gui import SearchApp

if __name__ == "__main__":
    multiprocessing.freeze_support()
    try:
        app = SearchApp()
        app.mainloop()
    except Exception as e:
        logging.critical(f"Erro fatal na aplicação: {e}", exc_info=True)
