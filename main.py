from functions.run_pipeline.pipeline import lambda_handler as run_pipeline
import logging

# Set level INFO, DEBUG etc. for local environment
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    run_pipeline(None, None)
