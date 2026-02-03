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
        image="python:3.11-slim",
        file_name="main.py",
        compile_cmd=None,
        run_cmd=["python", "main.py"]
    ),

    "cpp:gcc-12": Runtime(
        name="cpp:gcc-12",
        image="gcc:12",
        file_name="main.cpp",
        compile_cmd=[
            "g++", "main.cpp",
            "-std=c++17",
            "-O2",
            "-o", "main"
        ],
        run_cmd=["./main"],
    ),

    "node:18": Runtime(
        name="node:18",
        image="node:18-slim",
        file_name="main.js",
        compile_cmd=None,
        run_cmd=["node", "main.js"],
    ),
    
    "c:gcc-12": Runtime(
        name="c:gcc-12",
        image="gcc:12",         # Тот же образ, что и у C++
        file_name="main.c",
        compile_cmd=[
            "gcc", "main.c",
            "-O2",
            "-o", "main"
        ],
        run_cmd=["./main"],
    )
}
