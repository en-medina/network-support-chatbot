from typing import List, Tuple
from pydantic import BaseModel, Field, model_validator

class PlanExecute(BaseModel):
    plan: List[str] = Field(description="List of steps to execute to reach the final answer")

class RePlan(BaseModel):
    plan: List[str] = Field(description="List of steps to re-evaluate and potentially modify the original plan")
    response: str = Field(description="The response to the user based on the re-evaluated plan")
    action : str = Field(description="The action to take: either 'replan' or 'respond'")