import socket
import struct
import subprocess
from neo4j import GraphDatabase

MAGIC = b"\x60\x60\xb0\x17"

def get_listening_ports():
    try:
        output = subprocess.check_output("netstat -ano", shell=True).decode()
        ports = set()
        for line in output.splitlines():
            if "LISTENING" in line and "TCP" in line:
                parts = line.split()
                # Local address is usually parts[1]
                addr = parts[1]
                if ":" in addr:
                    port = addr.split(":")[-1]
                    if port.isdigit():
                        ports.add(int(port))
        return list(ports)
    except Exception as e:
        print(f"Error getting ports: {e}")
        return []

def test_ports():
    ports_to_test = get_listening_ports()
    print(f"Testing {len(ports_to_test)} listening ports...")
    
    found_port = None
    for port in ports_to_test:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.2)
            s.connect(('127.0.0.1', port))
            s.sendall(MAGIC)
            response = s.recv(4)
            s.close()
            if len(response) == 4:
                val = struct.unpack(">I", response)[0]
                # Valid Bolt protocol versions
                if val in (1, 2, 3, 4, 5, 401, 501, 502, 503, 504):
                    print(f"Port {port} looks like a Bolt server! (Version {val})")
                    found_port = port
                    break
        except Exception as e:
            pass
            
    if found_port:
        print(f"\nAttempting to connect to bolt://localhost:{found_port}")
        try:
            driver = GraphDatabase.driver(f"bolt://localhost:{found_port}", auth=("", ""))
            with driver.session() as session:
                res = session.run("RETURN 1 AS test")
                print(f"Query returned: {res.single()['test']}")
                print("SUCCESS!")
            # Also try to fetch the database version to confirm it's Memgraph
            with driver.session() as session:
                try:
                    res = session.run("CALL db.version() YIELD version RETURN version")
                    print(f"DB Version: {res.single()['version']}")
                except:
                    pass
        except Exception as e:
            print(f"Driver connection failed: {e}")
            
        print("\nRecommended Environment Variables:")
        print(f"MEMGRAPH_URI=bolt://localhost:{found_port}")
        print("MEMGRAPH_USERNAME=")
        print("MEMGRAPH_PASSWORD=")
    else:
        print("No Bolt server found on the scanned ports.")

if __name__ == "__main__":
    test_ports()
