from __future__ import annotations

import csv
import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import Optional

PID_FILE = Path(__file__).resolve().parent.parent / "data" / "capture.pid"
DEFAULT_OUTPUT = Path(__file__).resolve().parent.parent / "data" / "live_traffic.csv"


def _bootstrap_csv(output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    if not output_file.exists() or output_file.stat().st_size == 0:
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["src_ip", "dst_ip", "protocol", "src_port", "dst_port", "length"],
            )
            writer.writeheader()


def packet_callback(packet, output_file: Path) -> None:
    from scapy.all import IP, TCP, UDP  # lazy import

    protocol_value = ""
    if IP in packet:
        proto_num = packet[IP].proto
        protocol_value = {6: "TCP", 17: "UDP", 1: "ICMP"}.get(proto_num, str(proto_num))

    fields = {
        "src_ip": packet[IP].src if IP in packet else "",
        "dst_ip": packet[IP].dst if IP in packet else "",
        "protocol": protocol_value,
        "src_port": packet[TCP].sport if TCP in packet else packet[UDP].sport if UDP in packet else "",
        "dst_port": packet[TCP].dport if TCP in packet else packet[UDP].dport if UDP in packet else "",
        "length": len(packet),
    }

    with open(output_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields.keys())
        writer.writerow(fields)


def run_sniffer(output_file: str, iface: Optional[str] = None, packet_count: int = 0) -> None:
    from scapy.all import sniff

    target = Path(output_file).resolve()
    _bootstrap_csv(target)
    sniff(
        prn=lambda packet: packet_callback(packet, target),
        store=0,
        iface=iface,
        count=packet_count if packet_count > 0 else 0,
    )


def _is_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def capture_status() -> dict:
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            return {"running": _is_running(pid), "pid": pid}
        except Exception:
            return {"running": False, "pid": None}
    return {"running": False, "pid": None}


def start_capture(output_file: str | Path = DEFAULT_OUTPUT, iface: Optional[str] = None, packet_count: int = 0) -> str:
    status = capture_status()
    if status["running"]:
        return f"Захват уже запущен (PID {status['pid']})"

    target = Path(output_file).resolve()
    _bootstrap_csv(target)
    cmd = [sys.executable, __file__, "--run-sniffer", "--output", str(target)]
    if iface:
        cmd.extend(["--iface", iface])
    if packet_count > 0:
        cmd.extend(["--count", str(packet_count)])

    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    PID_FILE.write_text(str(proc.pid), encoding="utf-8")
    return f"Захват запущен (PID {proc.pid})"


def stop_capture() -> str:
    status = capture_status()
    pid = status.get("pid")
    if not pid or not status.get("running"):
        if PID_FILE.exists():
            PID_FILE.unlink(missing_ok=True)
        return "Захват не запущен"

    try:
        os.kill(pid, signal.SIGTERM)
        PID_FILE.unlink(missing_ok=True)
        return f"Захват остановлен (PID {pid})"
    except OSError as exc:
        return f"Не удалось остановить процесс: {exc}"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--run-sniffer", action="store_true")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--iface", default=None)
    parser.add_argument("--count", type=int, default=0)
    args = parser.parse_args()

    if args.run_sniffer:
        run_sniffer(args.output, args.iface, args.count)
