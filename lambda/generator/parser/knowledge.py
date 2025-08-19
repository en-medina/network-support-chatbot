from pydantic import BaseModel, Field, model_validator
from typing import Optional

class KnowledgeRankParser(BaseModel):
    question: str = Field(description="The input question you must answer")
    thought: str = Field(default=None, description="Thought process behind the answer.Explain your reasoning in a step-by-step manner to ensure your reasoning and conclusion are correct.")
    score: int = Field(description="Return an integer from 0 to 10. Do not provide any additional explanation or context.")

    # --- First validator: unwrap "properties" if the LLM wrapped output ---
    @model_validator(mode="before")
    @classmethod
    def unwrap_properties(cls, values):
        if isinstance(values, dict) and "properties" in values:
            return values["properties"]
        return values

    @model_validator(mode="before")
    @classmethod
    def validate_score(cls, values):
        if "properties" in values:
            values = values.get("properties", values)
        score = values.get("score")
        if score is None:
            raise ValueError("Score is required.")
        try:
            score = int(score)
        except ValueError:
            raise ValueError("Invalid score. Must be a number.")
        if not (0 <= score <= 10):
            raise ValueError("Invalid score. Must be between 0 and 10.")
        return values

class KnowledgeQAParser(BaseModel):
    question: str = Field(description="The input question you must answer")
    action: Optional[str] = Field(default=None, description="Action to take, either 'respond' or 'escalate'")
    final_answer: str = Field(description="The final answer to the question. Provide a clear and concise answer based solely on the CONTEXT")

    # --- First validator: unwrap "properties" if the LLM wrapped output ---
    @model_validator(mode="before")
    @classmethod
    def unwrap_properties(cls, values):
        if "properties" in values:
            return values["properties"]
        return values

    # --- Second validator: enforce valid action values ---
    @model_validator(mode="before")
    @classmethod
    def validate_action(cls, values):
        if "properties" in values:
            values = values.get("properties", values)
        action = values.get("action")
        if action not in ["respond", "escalate"]:
            raise ValueError("Invalid action. Must be 'respond' or 'escalate'.")
        return values
