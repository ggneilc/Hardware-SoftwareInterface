if command -v python >/dev/null 2>&1; then
    PYTHON_EXEC="python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_EXEC="python3"
elif command -v py >/dev/null 2>&1; then
    PYTHON_EXEC="py"
else
    echo "Python is not installed"
    exit 1
fi

$PYTHON_EXEC disasm.py $1