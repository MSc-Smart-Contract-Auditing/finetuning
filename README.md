# finetuning
Pipeline for finetuning LLMs


## Usage
1. Set up two environment variables (recommended to do this inside the terminal config):
- `export ICL_USERNAME={imperial_username}`
- `export ICL_PASSWORD={imperial_password}`

2. Run script `./start-job.sh` to reserve a job.

3. Run script `./run-server.sh -p {PORT} -e {ENV}` to start a Jupyter server on `PORT` running your `{ENV}` python environment.


## Formal Verification
This repo contains a Web application which goes through model outputs and allows for manual labeling of the results.

The accuracy of the evaluating model is then approximated using a Sequential Massart algorithm (See: `formal-verification/sequential_massart_smc.ipynb`

To ensure good estimate of the model accuracy at least a 100 rows need to be evaluated.

### Runnnig the web app

1. Run `make install`

2. Run `make run` to start the app
