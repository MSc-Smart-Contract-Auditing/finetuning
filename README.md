# finetuning
Pipeline for finetuning LLMs


### Usage
1. Set up two environment variables (recommended to do this inside the terminal config):
- `export ICL_USERNAME={imperial_username}`
- `export ICL_PASSWORD={imperial_password}`

2. Run script `./start-job.sh` to reserve a job.

3. Run script `./run-server.sh -p {PORT} -e {ENV}` to start a Jupyter server on `PORT` running your `{ENV}` python environment.