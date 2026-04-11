import os

# Define the single source of truth
REAL_DB = os.path.normpath("d:/Sebastian/Dokumente/Privat/Maria/Arbeit/GynOrg/backend/data/gynorg.db")

# Define files to move to backup if they exist
CANDIDATES = [
    "d:/Sebastian/Dokumente/Privat/Maria/Arbeit/GynOrg/gynorg.db",
    "d:/Sebastian/Dokumente/Privat/Maria/Arbeit/GynOrg/backend/app.db",
    "d:/Sebastian/Dokumente/Privat/Maria/Arbeit/GynOrg/data/gynorg.db", # Root data folder
    "d:/Sebastian/Dokumente/Privat/Maria/Arbeit/GynOrg/app.db"
]

def consolidate():
    print(f"Active Single Source of Truth: {REAL_DB}")
    if not os.path.exists(REAL_DB):
        print(f"CRITICAL ERROR: The 'Real' DB does not exist at {REAL_DB}")
        return

    for path in CANDIDATES:
        path = os.path.normpath(path)
        if path == REAL_DB:
            print(f"Skipping active DB: {path}")
            continue
            
        if os.path.exists(path):
            bak_path = path + ".bak"
            try:
                if os.path.exists(bak_path):
                     os.remove(bak_path) # Overwrite old backup
                os.rename(path, bak_path)
                print(f"MOVED: {path} -> {bak_path}")
            except Exception as e:
                print(f"ERROR moving {path}: {e}")
        else:
            print(f"Not found (clean): {path}")

if __name__ == "__main__":
    consolidate()
