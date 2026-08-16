import os
from dotenv import load_dotenv

def verify_env():
    # Attempt to load .env from the current directory
    loaded = load_dotenv()
    if not loaded:
        print("Failed to load .env file")
        return
        
    uri = os.environ.get("NEO4J_URI")
    username = os.environ.get("NEO4J_USERNAME")
    password = os.environ.get("NEO4J_PASSWORD")
    database = os.environ.get("NEO4J_DATABASE")
    
    print(f"- NEO4J_URI configured: {'YES' if uri else 'NO'}")
    print(f"- NEO4J_USERNAME configured: {'YES' if username else 'NO'}")
    print(f"- NEO4J_PASSWORD configured: {'YES' if password else 'NO'}")
    print(f"- NEO4J_DATABASE configured: {'YES' if database else 'NO'}")

if __name__ == "__main__":
    verify_env()
