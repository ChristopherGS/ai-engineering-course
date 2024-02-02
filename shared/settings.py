from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
N_GPU_LAYERS = 4

# Models
MISTRAL_7B_FILE = "mistral-7b-instruct-v0.2.Q4_K_M.gguf"
MIXTRAL_7B_FILE = "Mixtral_8x7B_Instruct_v0.1.gguf"
