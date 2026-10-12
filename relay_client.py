"""Discovery and one-click payload delivery for the PS5 Doctor relay."""
from __future__ import annotations

import ipaddress
import socket
import time
from pathlib import Path
from typing import Iterable

DISCOVERY_PORT = 10103
RELAY_PORT = 10102
LOADER_PORT = 9021
DISCOVERY_REQUEST = b"PS5JD_DISCOVER_V1"
DISCOVERY_PREFIX = "PS5JD_RELAY_V1"
RELAY_ELF_NAME = "PS5JailbreakDoctorRelay.elf"
MAX_RELAY_ELF_SIZE = 16 * 1024 * 1024


def preferred_connection_mode(settings: dict) -> str:
    """Default new/legacy installations to the relay; preserve explicit user choice."""
    mode = settings.get("connection_mode")
    return mode if mode in ("relay", "direct") else "relay"


def preferred_connection_port(settings: dict, mode: str) -> str:
    """Return the correct default port without carrying a legacy direct port into relay mode."""
    if mode == "relay":
        return str(RELAY_PORT)
    return str(settings.get("port", 10101))


class RelayError(RuntimeError):
    """A relay could not be located, loaded, or validated."""


def _is_trusted_lan_ipv4(address: ipaddress.IPv4Address) -> bool:
    """Mirror the relay's private/shared IPv4 allow-list."""
    allowed = (
        ipaddress.ip_network("10.0.0.0/8"),
        ipaddress.ip_network("172.16.0.0/12"),
        ipaddress.ip_network("192.168.0.0/16"),
        ipaddress.ip_network("100.64.0.0/10"),
    )
    return any(address in network for network in allowed)


def parse_discovery_reply(data: bytes, source_ip: str) -> tuple[str, int] | None:
    """Validate relay discovery payload and return (source IP, TCP port)."""
    try:
        message = data.decode("ascii", errors="strict").strip()
        parsed_source = ipaddress.ip_address(source_ip)
    except (UnicodeDecodeError, ValueError):
        return None
    if not isinstance(parsed_source, ipaddress.IPv4Address) or not _is_trusted_lan_ipv4(parsed_source):
        return None
    source = str(parsed_source)
    fields = message.split()
    if len(fields) < 2 or fields[0] != DISCOVERY_PREFIX:
        return None
    port_value = None
    for field in fields[1:]:
        if field.startswith("port="):
            port_value = field.partition("=")[2]
            break
    try:
        port = int(port_value or "")
    except ValueError:
        return None
    if not 1 <= port <= 65535:
        return None
    return source, port


def _local_ipv4_addresses() -> set[str]:
    """Return likely LAN IPv4 addresses without third-party dependencies."""
    values: set[str] = set()
    candidates = [socket.gethostname(), socket.getfqdn()]
    for host in candidates:
        try:
            for item in socket.getaddrinfo(host, None, socket.AF_INET, socket.SOCK_DGRAM):
                addr = item[4][0]
                ip = ipaddress.ip_address(addr)
                if ip.version == 4 and _is_trusted_lan_ipv4(ip) and not ip.is_loopback and not ip.is_link_local:
                    values.add(addr)
        except OSError:
            continue
    # This route-based lookup often finds Windows' active interface even when its
    # hostname does not resolve to a LAN address. UDP connect emits no packet.
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("192.0.2.1", 9))
        addr = probe.getsockname()[0]
        ip = ipaddress.ip_address(addr)
        if ip.version == 4 and _is_trusted_lan_ipv4(ip) and not ip.is_loopback and not ip.is_link_local:
            values.add(addr)
    except OSError:
        pass
    finally:
        probe.close()
    return values


def discovery_targets() -> list[str]:
    """Build global and common /24 directed-broadcast targets, plus local IPs."""
    targets = {"255.255.255.255"}
    for address in _local_ipv4_addresses():
        try:
            # Most home networks use /24. Global broadcast remains available as a
            # fallback for other subnets. Discovery always has a manual-IP fallback.
            network = ipaddress.ip_network(f"{address}/24", strict=False)
            targets.add(str(network.broadcast_address))
        except ValueError:
            continue
    return sorted(targets)


def discover_relay(timeout: float = 2.0, targets: Iterable[str] | None = None) -> tuple[str, int] | None:
    """Find a relay with UDP broadcast. Returns its IPv4 address and TCP port."""
    duration = max(0.2, min(float(timeout), 15.0))
    destinations = list(targets) if targets is not None else discovery_targets()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(("0.0.0.0", 0))
        for target in destinations:
            try:
                sock.sendto(DISCOVERY_REQUEST, (target, DISCOVERY_PORT))
            except OSError:
                # Windows firewall or a network adapter may reject one broadcast;
                # try the remaining targets rather than abort discovery.
                continue
        deadline = time.monotonic() + duration
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return None
            sock.settimeout(remaining)
            try:
                data, address = sock.recvfrom(1024)
            except socket.timeout:
                return None
            except OSError as exc:
                raise RelayError(f"A procura do relay falhou: {exc}") from exc
            found = parse_discovery_reply(data, address[0])
            if found:
                return found
    finally:
        sock.close()


def find_relay_elf() -> Path:
    """Find the relay ELF bundled by CI or built from source."""
    import sys

    candidates = []
    if getattr(sys, "_MEIPASS", None):
        candidates.append(Path(sys._MEIPASS) / "payloads" / RELAY_ELF_NAME)
    here = Path(__file__).resolve().parent
    candidates.extend([
        here / "payloads" / RELAY_ELF_NAME,
        here / "ps5-relay" / "build" / RELAY_ELF_NAME,
        here / "ps5-relay" / RELAY_ELF_NAME,
        here.parent / "payloads" / RELAY_ELF_NAME,
    ])
    for candidate in candidates:
        if candidate.is_file() and 4 <= candidate.stat().st_size <= MAX_RELAY_ELF_SIZE:
            return candidate
    raise RelayError(
        "O relay ELF ainda não está incluído nesta compilação. Usa a versão gerada pelo workflow de Windows + PS5 relay, "
        "ou carrega PS5JailbreakDoctorRelay.elf através do menu de payloads do etaHEN."
    )


def send_relay_elf(host: str, elf_path: str | Path | None = None, port: int = LOADER_PORT,
                   timeout: float = 5.0) -> int:
    """Send the bundled ELF as a raw payload to a compatible PS5 ELF loader."""
    try:
        ip = ipaddress.ip_address(host.strip())
    except ValueError as exc:
        raise RelayError("Indica o IP IPv4 atual da PS5 para carregar o relay.") from exc
    if ip.version != 4 or ip.is_loopback or ip.is_unspecified or ip.is_multicast or not _is_trusted_lan_ipv4(ip):
        raise RelayError("O endereço da PS5 tem de ser um IPv4 privado da rede local; não será enviado um ELF para endereços públicos.")
    path = Path(elf_path) if elf_path else find_relay_elf()
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise RelayError(f"Não foi possível ler o relay ELF: {exc}") from exc
    if not (4 <= len(payload) <= MAX_RELAY_ELF_SIZE) or payload[:4] != b"\x7fELF":
        raise RelayError("O relay ELF está vazio, é demasiado grande ou não tem uma assinatura ELF válida.")
    try:
        with socket.create_connection((str(ip), int(port)), timeout=timeout) as conn:
            conn.settimeout(timeout)
            conn.sendall(payload)
            try:
                conn.shutdown(socket.SHUT_WR)
            except OSError:
                pass
    except OSError as exc:
        raise RelayError(
            f"Não foi possível enviar o payload para {ip}:{port}: {exc}. Confirma que o loader de payloads está ativo "
            "na PS5 (normalmente porta 9021) e que o PC está na mesma rede."
        ) from exc
    return len(payload)
