# tutor/config.py
BEHAVIOUR_MODEL_CHOICE = "ednet"  # "ednet" or "oulad"

BEHAVIOUR_MODELS = {
    "ednet": {
        "model": "external/models/behavior/ednet_lstm_v1/model.h5",
        "preproc": "external/models/behavior/ednet_lstm_v1/preproc.pkl",
    },
    "oulad": {
        "model": "external/models/behavior/oulad_lstm_v1/model.h5",
        "preproc": "external/models/behavior/oulad_lstm_v1/preproc.pkl",
    }
}

BEHAV_SEQ_LEN = 20