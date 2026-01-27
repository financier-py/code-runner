from typing import Literal
from pydantic import BaseModel, Field

class RunRequest(BaseModel):
    runtime: str
    code: str = Field(..., max_length=1000)
    stdin: str = Field(default="", max_length=1000)

class RunResult(BaseModel):
    stdout: str
    stderr: str
    returncode: int | None
    status: Literal[
        "queued",
        "running",
        "finished",
        "compile_error",
        "runtime_error",
        "timeout",
        "error"
    ]

class Job(BaseModel):
    id: str
    runtime: str
    code: str
    stdin: str
    result: RunResult | None = None