from pydantic import BaseModel, Field

class AiSuggestionResponse(BaseModel):
    """AI suggestion response model."""

    id: int = Field(..., description="The suggestion ID", example=1)
    user_id: int = Field(..., description="The ID of the user who requested the suggestion", example=42)
    prompt: str = Field(..., description="The user's prompt", example="What is the capital of France?")
    suggestion: str = Field(..., description="The AI's suggested response", example="The capital of France is Paris.")
    created_at: str = Field(..., description="The timestamp when the suggestion was created", example="2023-01-01T00:00:00Z")