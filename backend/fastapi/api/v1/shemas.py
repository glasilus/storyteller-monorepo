from pydantic import BaseModel, Field

class ScriptRequest(BaseModel):
    promt: str | None = Field(max_lenght = 100)
    style: str | None = Field(max_lenght = 50)
    time: float | None = Field(ge = 0, le = 300)