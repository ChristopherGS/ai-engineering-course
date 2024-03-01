## Modal Setup

1. Create and activate virtualenv
2. `pip install modal`
3. Go to [modal.com](https://modal.com/) and sign up. Leave the browser open.
4. Run `modal token new` - this will write your modal token to your `.modal.toml` file
on disk (e.g. on MacOS mine is here: `/Users/christophersamiullah/.modal.toml`)

For using GPUs
5. Run `modal deploy inference.py` - this will deploy the inference.py file to the modal server


## Basic Inference Setup
- Create and activate venv
- `pip install -r requirements.txt`
- Create [together AI](https://api.together.xyz/docs) account and get API key
- Add `TOGETHER_API_KEY` to environment variables (or use [dotenv](https://pypi.org/project/python-dotenv/) library)
- Run `PYTHONPATH=. python app/main.py`
- Navigate to `http://0.0.0.0:8001/docs` and try out the interactive mode for inference