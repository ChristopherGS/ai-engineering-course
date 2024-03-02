## Basic Inference Setup
- Create and activate venv
- `pip install -r requirements.txt`
- Create [together AI](https://api.together.xyz/docs) account and get API key
- Add `TOGETHER_API_KEY` to environment variables (or use [dotenv](https://pypi.org/project/python-dotenv/) library)
- Run `PYTHONPATH=. python app/main.py`
- Navigate to `http://0.0.0.0:8001/docs` and try out the interactive mode for inference