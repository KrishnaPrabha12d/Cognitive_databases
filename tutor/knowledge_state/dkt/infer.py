import os
import json
import torch
import torch.nn as nn

# -------------------------------
# DKT Model Definition (Inference)
# -------------------------------
class DKT(nn.Module):
    def __init__(self, num_items: int, embed_dim: int = 64, hidden_dim: int = 128):
        super().__init__()
        self.num_items = num_items
        self.num_interactions = num_items * 2

        self.embedding = nn.Embedding(self.num_interactions, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True)
        self.dropout = nn.Dropout(0.2)
        self.fc = nn.Linear(hidden_dim, num_items)

    def forward(self, inter_ids: torch.Tensor, target_item_ids: torch.Tensor) -> torch.Tensor:
        emb = self.embedding(inter_ids)
        lstm_out, _ = self.lstm(emb)
        lstm_out = self.dropout(lstm_out)
        logits_all = self.fc(lstm_out)
        logits = torch.gather(logits_all, 2, target_item_ids.unsqueeze(-1)).squeeze(-1)
        return logits


# -------------------------------
# DKT Inference Wrapper
# -------------------------------
class DKTInference:
    """
    Keeps per-student interaction memory and predicts mastery for a given next item/skill.
    """
    def __init__(self, model_dir: str, device: str | None = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        model_path = os.path.join(model_dir, "model.pt")
        mapping_path = os.path.join(model_dir, "id_map.json")

        # Load item mapping (assumes dict: item_id(str) -> index(int))
        with open(mapping_path, "r", encoding="utf-8") as f:
            self.item2id = json.load(f)

        # If your json is id->item, flip it (safe handling)
        # Detect by checking if first value looks like a string
        try:
            first_val = next(iter(self.item2id.values()))
            if isinstance(first_val, str):
                # it's id->item, so invert
                self.item2id = {v: int(k) for k, v in self.item2id.items()}
        except StopIteration:
            raise ValueError("id_map.json is empty")

        self.num_items = len(self.item2id)

        # Load model
        self.model = DKT(num_items=self.num_items).to(self.device)

        checkpoint = torch.load(model_path, map_location=self.device)

        # Your checkpoint uses "model_state_dict"
        if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
            self.model.load_state_dict(checkpoint["model_state_dict"])
        else:
            # fallback: checkpoint itself might be a state_dict
            self.model.load_state_dict(checkpoint)

        self.model.eval()

        # Per-student state memory: user_id -> [interaction_ids]
        self.student_states: dict[str, list[int]] = {}

    def update_state(self, user_id: str, item_id: str, correct: int | bool):
        """
        Stores interaction history for a student.
        item_id must exist in item2id mapping.
        """
        if item_id not in self.item2id:
            return

        item_idx = int(self.item2id[item_id])
        correct = int(correct)

        # interaction id encoding (same as your training):
        # incorrect => item_idx
        # correct   => item_idx + num_items
        inter_id = item_idx + (correct * self.num_items)

        seq = self.student_states.setdefault(user_id, [])
        seq.append(inter_id)

        # keep last 200 interactions
        if len(seq) > 200:
            self.student_states[user_id] = seq[-200:]

    def predict_next(self, user_id: str, next_item_id: str) -> float:
        """
        Returns mastery probability for next_item_id.
        """
        if user_id not in self.student_states:
            return 0.5
        if next_item_id not in self.item2id:
            return 0.5

        inter_seq = self.student_states[user_id]
        target_item = int(self.item2id[next_item_id])

        inter_tensor = torch.tensor(inter_seq, dtype=torch.long).unsqueeze(0).to(self.device)

        target_tensor = torch.tensor(
            [target_item] * len(inter_seq),
            dtype=torch.long
        ).unsqueeze(0).to(self.device)

        with torch.no_grad():
            logits = self.model(inter_tensor, target_tensor)
            prob = torch.sigmoid(logits[:, -1]).item()

        return float(prob)


# -------------------------------
# Global loaders (so website can use easily)
# -------------------------------
_BASE = os.path.join("external", "models", "dkt")
_ENGINES: dict[str, DKTInference] = {}

def get_engine(model_key: str = "ednet_v1") -> DKTInference:
    """
    model_key: 'ednet_v1' or 'assistments_v1'
    """
    if model_key not in _ENGINES:
        model_dir = os.path.join(_BASE, model_key)
        _ENGINES[model_key] = DKTInference(model_dir=model_dir)
    return _ENGINES[model_key]

def predict_mastery(user_id: str, next_item_id: str, model_key: str = "ednet_v1") -> float:
    """
    Simple website-friendly call:
    returns mastery probability for next_item_id.
    """
    engine = get_engine(model_key)
    return engine.predict_next(user_id, next_item_id)

def update_interaction(user_id: str, item_id: str, correct: int | bool, model_key: str = "ednet_v1"):
    """
    Website call after a question attempt.
    """
    engine = get_engine(model_key)
    engine.update_state(user_id, item_id, correct)