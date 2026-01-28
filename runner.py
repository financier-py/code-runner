import subprocess
import tempfile
import uuid
import os
from pathlib import Path

from models import RunResult
from runtimes import RUNTIMES, Runtime

# Используем директорию для обмена с sandbox контейнерами
# Если worker запущен в Docker, эта директория должна быть смонтирована с хоста
SANDBOX_WORKDIR = Path(os.environ.get("SANDBOX_WORKDIR", "/tmp/code_runner_sandbox"))

def _docker_run(
        image: str,
        command: list[str],
        workdir: Path,
        stdin: str = "",
        timeout: int = 5
) -> subprocess.CompletedProcess:
    container_name = f"sandbox-{uuid.uuid4()}"

    cmd = [
        "docker", "run", "--rm",
        "-i",
        "--name", container_name, 
        "--memory=64m", "--cpus=1",
        "--pids-limit=32", "--network=none",
        "--read-only", "--cap-drop=ALL",
        "--tmpfs", "/tmp",
        "-v", f"{workdir}:/sandbox",
        "-w", "/sandbox",
        image,
        *command
    ]
    try:
        return subprocess.run(
            cmd,
            input=stdin,
            text=True,
            capture_output=True, 
            timeout=timeout
        )
    except subprocess.TimeoutExpired:
        subprocess.run(
            ["docker", "kill", container_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        raise

def run_job(runtime_name: str, code: str, stdin: str) -> RunResult:
    runtime: Runtime | None = RUNTIMES.get(runtime_name)
    if runtime is None: 
        return RunResult(
            stdout="", 
            stderr=f"Unsupported runtime: {runtime_name}",
            returncode=None,
            status="error"
        )
    
    # Создаём временную директорию внутри SANDBOX_WORKDIR
    # Это нужно, чтобы путь был доступен как на хосте, так и в worker контейнере
    SANDBOX_WORKDIR.mkdir(parents=True, exist_ok=True)
    
    with tempfile.TemporaryDirectory(dir=SANDBOX_WORKDIR) as tmpdir:
        sandbox = Path(tmpdir)
        
        # запишем код в наш файлик
        source_file = sandbox / runtime.file_name # перегруженный оператор / прикольно
        source_file.write_text(code)

        # скомпилим, если это там плюсы иил чето такое
        if runtime.compile_cmd is not None:
            try:
                compile_res = _docker_run(
                    image=runtime.image,
                    command=runtime.compile_cmd,
                    workdir=sandbox
                )
            except subprocess.TimeoutExpired:
                return RunResult(
                    stdout="",
                    stderr="Compilation timeout",
                    returncode=None,
                    status="compile_error"
                )
            
            if compile_res.returncode != 0:
                return RunResult(
                    stdout=compile_res.stdout,
                    stderr=compile_res.stderr,
                    returncode=compile_res.returncode,
                    status="compile_error"
                )
        
        # теперь запустим :)
        try:
            run_res = _docker_run(
                image=runtime.image,
                command=runtime.run_cmd,
                workdir=sandbox,
                stdin=stdin
            )
        except subprocess.TimeoutExpired:
            return RunResult(
                stdout="",
                stderr="Time limit exceeded",
                returncode=None,
                status="timeout"
            )
        
        status = "finished" if run_res.returncode == 0 else "runtime_error"
        return RunResult(
            stdout=run_res.stdout,
            stderr=run_res.stderr,
            returncode=run_res.returncode,
            status=status
        )