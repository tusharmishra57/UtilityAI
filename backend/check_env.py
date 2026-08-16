from dotenv import load_dotenv
import os
load_dotenv()
print("DATABASE_URL:", repr(os.getenv("DATABASE_URL")))
