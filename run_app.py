import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.StreamHandler(sys.stdout)
                    ])

# Load environment variables from .env file
logging.info("Loading environment variables from .env file...")
load_dotenv()

# Get the API key from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    logging.error("GROQ_API_KEY not found in .env file!")
    sys.exit(1)

logging.info(f"GROQ API key loaded successfully: {GROQ_API_KEY[:5]}...")

# Fix the initialization issue by patching the LLMManager class
def patch_llm_manager():
    try:
        from retriever.llm_manager import LLMManager
        from langchain_groq import ChatGroq
        
        # Store the original __init__ method
        original_init = LLMManager.__init__
        
        # Define a new __init__ method that ensures proper initialization
        def new_init(self):
            # Call the original __init__ first
            original_init(self)
            
            # Force-initialize the LLM if it's None
            if self.generation_llm is None:
                try:
                    # Try direct initialization
                    logging.info("Forcing direct LLM initialization...")
                    self.generation_llm = ChatGroq(
                        model="gemma2-9b-it",
                        temperature=0.7,
                        api_key=GROQ_API_KEY
                    )
                    self.generation_llm.name = "gemma2-9b-it"
                    logging.info("Generation LLM initialized by patch!")
                except Exception as e:
                    logging.error(f"Error in patched initialization: {str(e)}")
        
        # Replace the __init__ method
        LLMManager.__init__ = new_init
        logging.info("Successfully patched LLMManager")
        
    except Exception as e:
        logging.error(f"Failed to patch LLMManager: {str(e)}")

# Apply the patch
patch_llm_manager()

# Import and run the app
logging.info("Starting application with GROQ API key set...")
import app
logging.info("Application startup complete!") 