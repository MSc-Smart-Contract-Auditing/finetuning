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

### Runnnig the web app

1. Run `make install`

2. Run `make run` to start the app

### Results
In total `213` rows were verified where each row contains `3` criteria or `639` samples.

Below is the resulting accuracy of `gpt-4o-mini` for evaluating audits.

<img src="https://github.com/MSc-Smart-Contract-Audition/finetuning/blob/main/formal-verification/sequential_massart.png">

```bash
633: Interval: [0.9223155036427156, 0.9780027129062199] - Samples: 634.0 - Estimate: 0.9557661927330173
```

The model achieves an evaluation accuracy of $(95.6\pm 5)$\% with $97.6$\% confidence.

To be more exact the accuracy lays between $92.2$\% and $97.8$\% with $97.6$\% confidence. This means that the probability that the estimate is outside of this range is just $2.4$\%.
