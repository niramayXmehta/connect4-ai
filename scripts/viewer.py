import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.viewer.server import app


if __name__ == "__main__":
    print("Connect4 AI Viewer")
    print("Open http://localhost:5000")
    app.run(debug=False, port=5000)

