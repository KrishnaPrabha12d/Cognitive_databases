import torch
import torch.nn as nn

class DKTModel(nn.Module):
    """
    Deep Knowledge Tracing model that predicts a student's mastery of skills based on their past interactions.
    """
    def __init__(self, num_skills:int, embed_dim:int=32, hidden_dim: int = 64):
        """
        Initializes the SkillDKT model.

        Args:
            num_skills (int): The total number of unique skills.
            embed_dim (int): The dimensionality of the interaction embeddings.
            hidden_dim (int): The dimensionality of the LSTM hidden state.
        """
        super().__init__()
        self.num_skills = num_skills
        # Each skill can be answered correctly or incorrectly, so there are num_skills * 2 possible interactions.
        self.num_interactions = num_skills * 2

        # Embedding layer to convert interaction IDs into dense vectors.
        self.embedding = nn.Embedding(self.num_interactions, embed_dim)
        # LSTM layer to process the sequence of interaction embeddings.
        self.lstm = nn.LSTM(
            input_size=embed_dim,
            hidden_size=hidden_dim,
            batch_first=True
        )
        # Fully connected layer to predict the mastery probability for each skill.
        self.fc = nn.Linear(hidden_dim, num_skills)

    def forward(self, inter_ids, target_skill_ids):
        """
        Defines the forward pass of the model.

        Args:
            inter_ids (torch.Tensor): A tensor of shape [B, T] containing the sequence of interaction IDs.
            target_skill_ids (torch.Tensor): A tensor of shape [B, T] containing the target skill IDs for which to predict mastery.

        Returns:
            torch.Tensor: A tensor of shape [B, T] containing the predicted mastery logits for the target skills.
        """
        # Embed the interaction IDs.
        emb = self.embedding(inter_ids)
        # Pass the embeddings through the LSTM.
        lstm_out, _ = self.lstm(emb)
        # Pass the LSTM output through the fully connected layer to get logits for all skills.
        logits_all = self.fc(lstm_out)

        # Gather the logits for the specific target skills.
        logits = torch.gather(
            logits_all, 2, target_skill_ids.unsqueeze(-1)
        ).squeeze(-1)

        return logits

