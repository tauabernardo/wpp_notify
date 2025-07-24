#!/bin/bash

# Caminho absoluto ou relativo do projeto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Caminho do ambiente virtual
VENV_DIR="$PROJECT_DIR/venv"

# Ativar o ambiente virtual
source "$VENV_DIR/bin/activate"

# Rodar o script principal
python "$PROJECT_DIR/src/main.py"

# Encerrar o ambiente virtual após execução
deactivate
