from dataclasses import dataclass

@dataclass(frozen=True)
class Runtime:
    name: str
    image: str
    file_name: str
    compile_cmd: list[str] | None
    run_cmd: list[str]

RUNTIMES: dict[str, Runtime] = {
    "python:3.11": Runtime(
        name="python:3.11",
        image="sandbox-python:3.11",
        file_name="main.py",
        compile_cmd=None,
        run_cmd=["python", "main.py"]
    ),

    "cpp:gcc-12": Runtime(
        name="cpp:gcc-12",
        image="sandbox-cpp:gcc-12",
        file_name="main.cpp",
        compile_cmd=[
            "g++", "main.cpp",
            "-std=c++17",
            "-O2",
            "-o", "main"
        ],
        run_cmd=["./main"],
    )
}