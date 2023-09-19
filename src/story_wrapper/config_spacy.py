"""File to configure the spaCy processing pipeline."""
import os
import spacy
import logging

# Retrieve flag indicating whether GPU is enabled
GPU_ENABLED = os.environ.get('GPU_ENABLED', False)
# Retrieve variable indicating overwriting of the spacy model
# 'en_core_web_sm' is smaller but less accurate
# 'en_core_web_trf' is neural network and more accurate but slower
# See https://www.twilio.com/blog/environment-variables-python for further details
SPACY_MODEL = os.environ.get('SPACY_MODEL', 'en_core_web_trf')


def load_model():
    """Load the spacy model and configure the pipeline."""
    try:
        logging.info(f"Loading Spacy Model {SPACY_MODEL}")
        if GPU_ENABLED:
            logging.info(f"GPU Enabled: {GPU_ENABLED} - Using GPU")
            spacy.require_gpu()
        else:
            logging.info(f"GPU Enabled: {GPU_ENABLED} - GPU Off")
        nlp = spacy.load(SPACY_MODEL)
    except OSError as e:
        logging.warning(e)
        logging.warning("Spacy Model Load Error")
        # Attempt to download the model
        try:
            download_model(SPACY_MODEL)
            nlp = spacy.load(SPACY_MODEL)
        except Exception as e_download:
            logging.error(f"Could not download the model due to: {e_download}")
            logging.info("Falling back to 'en_core_web_sm'")
            nlp = spacy.load('en_core_web_sm')
    # Add custom components to the pipeline
    nlp = configure_pipeline(nlp)
    return nlp


def configure_pipeline(nlp):
    """Configure the spacy pipeline ."""
    # All these need to be after the dependency parse
    logging.debug("Configuring NLP Pipeline and Custom Properties")
    # Use nlp.add_pipe to add components to the pipeline
    return nlp


def download_model(model_name: str):
    """Download the spacy model."""
    logging.info(f"Downloading Spacy Model {model_name}")
    spacy.cli.download(model_name)


# See here - https://stackoverflow.com/questions/46249052/best-way-to-initialize-variable-in-a-module
class NLPService:
    """Service class to wrap the nlp object that consumes GPU resource."""
    nlp = None

    def get_nlp(self):
        """Get the nlp object."""
        if self.nlp is None:
            self.nlp = load_model()
        return self.nlp


nlp_service = NLPService()
