from crewai.utilities.paths import db_storage_path
import os

# Get the base storage path
storage_path = db_storage_path()
print(f"CrewAI storage location: {storage_path}")

# List all CrewAI storage directories
if os.path.exists(storage_path):
    print("\nStored files and directories:")
    for item in os.listdir(storage_path):
        item_path = os.path.join(storage_path, item)
        if os.path.isdir(item_path):
            print(f"📁 {item}/")
            # Show ChromaDB collections
            if os.path.exists(item_path):
                for subitem in os.listdir(item_path):
                    print(f"   └── {subitem}")
        else:
            print(f"📄 {item}")
else:
    print("No CrewAI storage directory found yet.")