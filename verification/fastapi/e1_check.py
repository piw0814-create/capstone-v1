"""E1 수동 검증 보조: 도구 호출 중 이 Backend 소유의 MCP만 종료합니다."""

import argparse
from datetime import datetime
import json
from pathlib import Path
import subprocess
import time
from urllib.request import urlopen

import psutil


ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
MCP_SCRIPT = str(ROOT / "mcp-server" / "server.py")
URL = "http://localhost:8000/chat"


def backend_listeners():
    result = subprocess.run(
        ["lsof", "-t", "-iTCP:8000", "-sTCP:LISTEN"],
        capture_output=True, text=True,
    )
    processes = []
    for value in set(result.stdout.split()):
        try:
            process = psutil.Process(int(value))
            if Path(process.cwd()).resolve() == BACKEND.resolve():
                processes.append(process)
        except (psutil.Error, ValueError):
            continue
    if not processes:
        raise SystemExit("이 프로젝트의 Backend가 8000 포트에서 실행 중인지 확인해 주세요.")
    return processes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="준비 상태만 확인; 요청·종료 없음")
    args = parser.parse_args()
    listeners = backend_listeners()
    with urlopen("http://localhost:8000/health", timeout=5) as response:
        assert json.load(response) == {"status": "ok"}
    print("Backend 연결 확인: 정상", flush=True)
    if args.check:
        print("준비 상태만 확인했습니다. MCP 종료와 AI 요청은 실행하지 않았습니다.")
        return

    request = {"message": "데이터베이스 다운 시 대응 절차를 운영 매뉴얼에서 검색해 주세요."}
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    output_dir = Path(__file__).resolve().parent
    body_file = output_dir / f"manual-E1-{stamp}-body.txt"
    report_file = output_dir / f"manual-E1-{stamp}.json"
    print("E1: 도구 호출 중 MCP 연결 중단", flush=True)
    print("POST", URL, flush=True)
    print("요청:", json.dumps(request, ensure_ascii=False), flush=True)
    call = subprocess.Popen(
        ["curl", "-sS", "--max-time", "90", "-o", str(body_file),
         "-w", "%{http_code}", "-X", "POST", URL,
         "-H", "Content-Type: application/json",
         "-d", json.dumps(request, ensure_ascii=False)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    killed_pid = None
    while call.poll() is None and killed_pid is None:
        for listener in listeners:
            try:
                children = listener.children(recursive=True)
            except psutil.Error:
                continue
            for child in children:
                try:
                    if MCP_SCRIPT in child.cmdline() and child.is_running():
                        child.kill()
                        killed_pid = child.pid
                        print("Backend 소유 MCP 종료: PID", killed_pid, flush=True)
                        break
                except psutil.Error:
                    continue
            if killed_pid is not None:
                break
        if killed_pid is None:
            time.sleep(0.05)
    status, error = call.communicate()
    body = body_file.read_text() if body_file.exists() else ""
    passed = killed_pid is not None and status.strip() == "500"
    report = {
        "request": request,
        "http_status": status.strip(),
        "killed_backend_mcp_pid": killed_pid,
        "response": body,
        "curl_error": error,
        "passed": passed,
        "method": "Kill only this Backend's descendant MCP during a tool call.",
    }
    report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print("HTTP 상태:", status.strip() or "응답 없음")
    print("응답:", body)
    print("E1 결과:", "PASS" if passed else "중단 오류가 재현되지 않았습니다. 결과를 확인해 주세요.")
    print("기록:", report_file.name)
    if error:
        print("요청 오류:", error.strip())
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
