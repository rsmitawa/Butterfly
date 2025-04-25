import subprocess
import sys
import os

def run_command(cmd, cwd=None):
    print(f"\n[RUN] {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        sys.exit(result.returncode)


def main():
    # Step 1: Check PDFs exist
    pdf_dir = os.path.join('data', 'raw')
    if not os.path.exists(pdf_dir) or not any(f.endswith('.pdf') for f in os.listdir(pdf_dir)):
        print(f"[ERROR] No PDFs found in {pdf_dir}. Please add PDF files to process.")
        sys.exit(1)
    print(f"[INFO] Found PDFs: {[f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]}")

    # Step 2: Build Docker images
    run_command(['docker-compose', 'build'])

    # Step 3: Start MongoDB and Ollama
    run_command(['docker-compose', 'up', '-d', 'mongodb', 'ollama'])

    # Step 4: Run PDF extraction & OCR (one-off)
    run_command([
        'docker-compose', 'run', '--rm', 'butterfly',
        'python', 'src/butterfly/rag/pdf_extractor.py'
    ])

    # Step 5: Start the web app
    run_command(['docker-compose', 'up', '-d', 'butterfly'])

    print("\n[INFO] Butterfly pipeline is ready! Access the app at http://localhost:5005\n")
    print("[INFO] To check MongoDB data, use MongoDB Compass or: docker exec -it mongodb mongosh\n")

if __name__ == "__main__":
    main()
