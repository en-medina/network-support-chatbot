from pydantic import BaseModel, Field, model_validator
from typing import Optional

class KnowledgeRankParser(BaseModel):
    question: str = Field(description="The input question you must answer")
    thought: str = Field(default=None, description="Thought process behind the answer.Explain your reasoning in a step-by-step manner to ensure your reasoning and conclusion are correct.")
    score: str = Field(description="Only return a score from 0 to 1. Do not provide any additional explanation or context.")

    @model_validator(mode="before")
    @classmethod
    def validate_score(cls, values):
        score = values.get("score")
        if score is None:
            raise ValueError("Score is required.")
        try:
            score = float(score)
        except ValueError:
            raise ValueError("Invalid score. Must be a number.")
        if not (0 <= score <= 1):
            raise ValueError("Invalid score. Must be between 0 and 1.")
        return values

class KnowledgeQAParser(BaseModel):
    question: str = Field(description="The input question you must answer")
    action: Optional[str] = Field(default=None, description="Action to take, either 'respond' or 'escalate'")
    final_answer: str = Field(description="The final answer to the question. Provide a clear and concise answer based solely on the CONTEXT")

    @model_validator(mode="before")
    @classmethod
    def validate_action(cls, values):
        action = values.get("action")
        if action not in ["respond", "escalate"]:
            raise ValueError("Invalid action. Must be 'respond' or 'escalate'.")
        return values
