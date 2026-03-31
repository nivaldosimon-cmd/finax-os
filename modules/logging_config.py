"""
Módulo de Logging Profissional - FINAX OS
Configuração centralizada de logging para toda a aplicação
"""

import logging
import sys
import os
from datetime import datetime

def setup_logging():
    """Configura o sistema de logging profissional com arquivo e console"""
    logger = logging.getLogger('finax_os')
    
    # Evitar múltiplos handlers
    if logger.hasHandlers():
        return logger
    
    logger.setLevel(logging.INFO)
    
    # Criar pasta de logs se não existir
    logs_dir = 'logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Formato profissional
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para arquivo com data
    log_filename = os.path.join(logs_dir, f"finax_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Adicionar handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Instância global
logger = setup_logging()

# Exportar para uso em outros módulos
__all__ = ['logger', 'setup_logging']
