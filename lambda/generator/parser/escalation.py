from pydantic import BaseModel, Field

class TaskParser(BaseModel):
    title: str = Field(description="Concise title summarizing the task.")
    description: str = Field(default=None, description="Detailed information about the task, including context or instructions.")
