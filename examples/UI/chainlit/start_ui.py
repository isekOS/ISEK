#!/usr/bin/env python3
"""
Startup script for ISEK Chainlit UI
This script helps you start both the agent server and Chainlit UI
"""

import subprocess
import sys
import time
import os
import socket
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import chainlit
        print("✅ Chainlit is installed")
    except ImportError:
        print("❌ Chainlit is not installed. Please run: pip install -r requirements.txt")
        return False
    
    try:
        from isek.node.node_v2 import Node
        print("✅ ISEK package is available")
    except ImportError:
        print("❌ ISEK Node not found. Please run: isek setup")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists"""
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
        return True
    else:
        print("❌ .env file not found")
        print("Please create a .env file with your OpenAI API credentials:")
        print("OPENAI_API_KEY=your_api_key_here")
        print("OPENAI_MODEL_NAME=gpt-4o-mini")
        print("OPENAI_BASE_URL=https://api.openai.com/v1")
        return False

def check_port_available(port):
    """Check if a port is available"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except OSError:
            return False

def kill_process_on_port(port):
    """Kill any process using the specified port"""
    try:
        result = subprocess.run(['lsof', '-ti', f':{port}'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    subprocess.run(['kill', '-9', pid], 
                                 capture_output=True, text=True)
                    print(f"✅ Killed process {pid} on port {port}")
                    time.sleep(1)  # Give it time to fully terminate
            return True
        return False
    except Exception as e:
        print(f"⚠️  Could not kill process on port {port}: {e}")
        return False

def ensure_port_available(port):
    """Ensure a port is available, killing any process using it if necessary"""
    if check_port_available(port):
        print(f"✅ Port {port} is available")
        return True
    
    print(f"⚠️  Port {port} is in use. Attempting to free it...")
    if kill_process_on_port(port):
        time.sleep(2)  # Wait for process to fully terminate
        if check_port_available(port):
            print(f"✅ Port {port} is now available")
            return True
        else:
            print(f"❌ Port {port} is still in use after killing process")
            return False
    else:
        print(f"❌ Could not free port {port}")
        return False

def start_server():
    """Start the agent server"""
    print("\n🚀 Starting ISEK Agent Server...")
    
    # Ensure port 9005 is available
    if not ensure_port_available(9005):
        print("❌ Could not free port 9005. Please manually stop any process using this port.")
        return None
    
    try:
        # Start the server in a subprocess
        dirc = os.path.dirname(__file__)
        server_process = subprocess.Popen([
            sys.executable, f"{dirc}/agent_server.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # Wait a moment for server to start
        time.sleep(3)
        
        if server_process.poll() is None:
            print("✅ Agent server started successfully")
            return server_process
        else:
            stdout, stderr = server_process.communicate()
            print(f"❌ Failed to start server: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return None

def start_chainlit():
    """Start the Chainlit UI"""
    print("\n🌐 Starting Chainlit UI...")
    
    # Ensure port 8000 is available for Chainlit
    if not ensure_port_available(8000):
        print("❌ Could not free port 8000. Please manually stop any process using this port.")
        return None
    
    try:
        # Start Chainlit in a subprocess
        dirc = os.path.dirname(__file__)
        chainlit_process = subprocess.Popen([
            sys.executable, "-m", "chainlit", "run", f"{dirc}/chainlit_app.py"
        ])
        
        time.sleep(2)
        
        if chainlit_process.poll() is None:
            print("✅ Chainlit UI started successfully")
            print("🌐 Open your browser to: http://localhost:8000")
            return chainlit_process
        else:
            print("❌ Failed to start Chainlit UI")
            return None
            
    except Exception as e:
        print(f"❌ Error starting Chainlit: {e}")
        return None

def main():
    """Main startup function"""
    print("🤖 ISEK Chainlit UI Startup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment file
    if not check_env_file():
        sys.exit(1)
    
    # Start server
    server_process = start_server()
    if not server_process:
        sys.exit(1)
    
    # Start Chainlit
    chainlit_process = start_chainlit()
    if not chainlit_process:
        server_process.terminate()
        sys.exit(1)
    
    print("\n🎉 Both services are running!")
    print("📝 Press Ctrl+C to stop both services")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if server_process.poll() is not None:
                print("❌ Agent server stopped unexpectedly")
                break
                
            if chainlit_process.poll() is not None:
                print("❌ Chainlit UI stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        
        # Terminate processes
        if server_process:
            server_process.terminate()
        if chainlit_process:
            chainlit_process.terminate()
        
        print("✅ Services stopped")

if __name__ == "__main__":
    main() 