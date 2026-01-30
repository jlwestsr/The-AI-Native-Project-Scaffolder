#!/bin/bash
set -e

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

echo "🚀 Bootstrapping Forge on ${MACHINE}..."

# Check Python Version favoring newer versions
if command -v python3.12 &>/dev/null; then
    PYTHON_CMD="python3.12"
elif command -v python3.11 &>/dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3.10 &>/dev/null; then
    PYTHON_CMD="python3.10"
elif command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
else
    echo "❌ Python 3 not found. Please install Python 3.10+."
    exit 1
fi

# Ensure Python version is sufficient (simple check for now)
PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "   Python version: ${PYTHON_VERSION}"

# Create Venv
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment in ${VENV_DIR}..."
    $PYTHON_CMD -m venv "$VENV_DIR"
else
    echo "📦 Virtual environment already exists."
fi

# Activate Venv for installation
source "${VENV_DIR}/bin/activate"

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install Dependencies
if [ -f "requirements.txt" ]; then
    echo "📚 Installing dependencies..."
    pip install -r requirements.txt
fi

if [ -f "requirements-dev.txt" ]; then
    echo "🛠️  Installing dev dependencies..."
    pip install -r requirements-dev.txt
fi

# Install Package in Editable Mode
echo "🔨 Installing Forge (editable mode)..."
pip install -e .

# Symlink to PATH
FORGE_BIN="$PWD/venv/bin/forge"
TARGET_DIR="$HOME/.local/bin"
TARGET_BIN="${TARGET_DIR}/forge"

# Detect if ~/.local/bin is in PATH
if echo "$PATH" | grep -q "$TARGET_DIR"; then
    IN_PATH=true
else
    IN_PATH=false
fi

echo "🔗 Setting up 'forge' command..."

# If ~/.local/bin exists or we can create it
if [ ! -d "$TARGET_DIR" ]; then
    mkdir -p "$TARGET_DIR"
fi

# Attempt to symlink to user bin
if [ -w "$TARGET_DIR" ]; then
    ln -sf "$FORGE_BIN" "$TARGET_BIN"
    echo "   ✅ Linked $FORGE_BIN -> $TARGET_BIN"
    
    if [ "$IN_PATH" = false ]; then
        echo "   ⚠️  Warning: $TARGET_DIR is not in your PATH."
        echo "   Please add the following to your shell config (.zshrc/.bashrc):"
        echo "   export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
else
    echo "   ⚠️  Cannot write to $TARGET_DIR. Trying global install (/usr/local/bin)..."
    GLOBAL_BIN="/usr/local/bin/forge"
    if sudo ln -sf "$FORGE_BIN" "$GLOBAL_BIN"; then
        echo "   ✅ Linked $FORGE_BIN -> $GLOBAL_BIN (Global)"
    else
        echo "   ❌ Failed to create symlink. You can run forge via:"
        echo "   ./venv/bin/forge"
    fi
fi

echo ""
echo "✨ Bootstrap complete! Try running: forge --help"
