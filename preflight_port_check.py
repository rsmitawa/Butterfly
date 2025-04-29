import socket
import sys

REQUIRED_PORTS = [
    (5005, 'Butterfly Web App'),
    (27017, 'MongoDB'),
    (11434, 'Ollama')
]

def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def main():
    conflict = False
    for port, desc in REQUIRED_PORTS:
        if check_port(port):
            print(f"WARNING: Port {port} ({desc}) is already in use! Please free it before starting the pipeline.")
            conflict = True
    if conflict:
        print("\nResolve the above port conflicts before running Docker Compose.")
        sys.exit(1)
    else:
        print("All required ports are free. Safe to start the pipeline.")

if __name__ == "__main__":
    main()
