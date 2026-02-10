from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class TutorAction:
    concept_id: str
    strategy: str      # maps to teaching_content.strategy (definition/example/exercise/...)
    hint_level: str    # low/normal/high
    reason: str


def decide_action(state: Dict[str, Any], concept_id: str) -> TutorAction:
    """
    concept_id: what you will query in teaching_content
    state: output of integrate_knowledge_state()
    """

    # mastery might be stored by skill_id in your app; if you use concept_id directly, keep same
    mastery_dict = state.get("mastery", {}) or {}
    # fallback: average if key missing
    mastery = float(mastery_dict.get(concept_id, state.get("overall_mastery", 0.5)))

    beh = state.get("behaviour", {}) or {}
    label = beh.get("label", "normal")
    mse = float(beh.get("mse", 0.0))

    # --- Decide strategy (maps to your DB column teaching_content.strategy) ---
    # low mastery -> definition, mid -> example, high -> exercise (if not exists, selector will fallback)
    if mastery < 0.6:
        strategy = "definition"
        kt_reason = f"Mastery {mastery:.2f} low → definition."
    elif mastery < 0.8:
        strategy = "example"
        kt_reason = f"Mastery {mastery:.2f} mid → example."
    else:
        strategy = "exercise"
        kt_reason = f"Mastery {mastery:.2f} high → exercise."

    # --- Decide hint level from behaviour ---
    if label == "warmup":
        hint_level = "normal"
        beh_reason = "Behaviour warmup → normal hints."
    elif label == "anomaly" or mse > 0.02:
        hint_level = "high"
        beh_reason = f"Behaviour anomaly/mse={mse:.4f} → high hints."
    else:
        hint_level = "low"
        beh_reason = f"Behaviour normal/mse={mse:.4f} → low hints."

    return TutorAction(
        concept_id=concept_id,
        strategy=strategy,
        hint_level=hint_level,
        reason=f"{kt_reason} {beh_reason}"
    )