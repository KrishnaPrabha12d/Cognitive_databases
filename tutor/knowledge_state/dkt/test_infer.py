from tutor.knowledge_state.dkt.infer import DKTInference

kt = DKTInference(
    model_dir="external/models/dkt/ednet_v1"
)

# Simulate a student answering a question
kt.update_state(user_id="765", item_id="q10648", correct=1)

# Predict mastery for the next question
p = kt.predict_next(user_id="765", next_item_id="q10647")

print("Predicted mastery probability:", p)