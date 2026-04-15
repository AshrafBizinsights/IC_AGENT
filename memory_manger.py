# memory_manager.py
from chromadb import PersistentClient

# Path to your Chroma memory directory
CHROMA_PATH = "./chroma_memory"

def list_memory_contents():
    client = PersistentClient(path=CHROMA_PATH)
    collections = client.list_collections()

    if not collections:
        print("🧠 No memory collections found.")
        return

    for col in collections:
        print(f"\n📂 Collection: {col.name}")
        collection = client.get_collection(name=col.name)
        results = collection.get()
        ids = results.get('ids', [])
        docs = results.get('documents', [])
        metadatas = results.get('metadatas', [])

        if not ids:
            print("   (empty)")
        else:
            for i, doc in enumerate(docs):
                print(f"  - ID: {ids[i]}")
                print(f"    Document: {doc}")
                if metadatas and metadatas[i]:
                    print(f"    Metadata: {metadatas[i]}")


def delete_all_memory():
    client = PersistentClient(path=CHROMA_PATH)
    collections = client.list_collections()

    if not collections:
        print("🧽 No memory to delete.")
        return

    for col in collections:
        print(f"🗑️ Deleting collection: {col.name}")
        client.delete_collection(name=col.name)

    print("✅ All memory collections deleted.")


def main():
    print("=== CrewAI Memory Manager ===")
    while True:
        print("\nOptions:")
        print("1. View memory contents")
        print("2. Delete all memory")
        print("3. Exit")

        choice = input("Enter choice (1/2/3): ").strip()

        if choice == "1":
            list_memory_contents()
        elif choice == "2":
            confirm = input("⚠️ Are you sure you want to delete all memory? (yes/no): ").strip().lower()
            if confirm == "yes":
                delete_all_memory()
            else:
                print("❌ Deletion cancelled.")
        elif choice == "3":
            print("👋 Exiting.")
            break
        else:
            print("❓ Invalid input. Try again.")

if __name__ == "__main__":
    main()
