import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'agents' / 'orchestrator'))

from main import orchestrator

if __name__ == "__main__":
    from google.adk.web import serve
    
    serve(
        agent=orchestrator,
        host="localhost",
        port=8000
    )
    
    print("\n" + "="*70)
    print("🌐 RecallOS Web UI Running!")
    print("="*70)
    print("Open: http://localhost:8000")
    print("="*70)