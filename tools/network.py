import platform
import subprocess
from datetime import datetime
from typing import Annotated, List
import socket

from langchain_core.tools import tool
from pydantic import BaseModel, Field

import dns.resolver
from dns import rdatatype
from whois import whois


PING_COUNT = 2
PING_TIMEOUT = 1  # seconds
PORT_CHECK_TIMEOUT = 1.0  # seconds, used in check_port function

def get_network_tools() -> List[tool]:
    """
    Returns a list of network-related tools that can be used for diagnostics.
    Each tool is defined with its name, description, and function.
    """
    return [ping_ip, check_port, query_dns_record, get_domain_metadata]

def get_network_tool_names() -> str:
    """
    Returns a comma-separated string of the names of all available network tools.
    """
    return ", ".join([tool.name for tool in get_network_tools()])


@tool
def ping_ip(ip_address: Annotated[str, "The IP address to ping."]) -> bool:
    """
    Pings an IP address using the system's ping command.
    Returns True if the host is reachable, otherwise False.
    """
    ping_count = PING_COUNT
    timeout_sec = PING_TIMEOUT
    app_os = platform.system().lower()

    # Determine the correct ping command based on the OS
    if app_os == "windows":
        # Windows uses -w in milliseconds
        command = [
            "ping",
            "-n",
            str(ping_count),
            "-w",
            str(timeout_sec * 1000),
            ip_address,
        ]
    else:
        # Linux/macOS use -W in seconds (and -c for ping_count)
        command = ["ping", "-c", str(ping_count), "-W", str(timeout_sec), ip_address]

    try:
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        output = result.stdout.lower()
        if app_os == "windows":
            return "ttl=" in output
        return "ttl=" in output or "bytes from" in output
    except Exception as e:
        print(f"Error executing ping: {e}")
        return False


@tool
def check_port(
    host: Annotated[str, "The hostname or IP address to check."],
    port: Annotated[int, "The port number to check."],
) -> bool:
    """
    Checks if a specific port on a host is open by attempting to connect to it.
    Returns True if the port is open, otherwise False.
    """

    timeout = PORT_CHECK_TIMEOUT
    sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sck.settimeout(timeout)
    try:
        sck.connect((host, int(port)))
        sck.shutdown(socket.SHUT_RDWR)
        return True
    except:
        return False
    finally:
        sck.close()


@tool
def query_dns_record(
    domain_name: Annotated[str, "The domain to query"],
    record_type: Annotated[
        str, "The DNS record type to query (e.g., 'A', 'MX', 'NS', 'TXT', etc.)"
    ],
) -> Annotated[
    List[str],
    "A list of DNS record data as strings. If no records are found or an error occurs, the list contains a single entry with the error messages.",
]:
    """
    Queries DNS records of a specified type for a given domain.
    Returns a list of record data or error messages if the query fails.
    """
    try:
        answers = dns.resolver.resolve(domain_name, record_type)
        answer = [rdata.to_text() for rdata in answers]
        return answer
    except dns.resolver.NoAnswer:
        return [f"No {record_type} records found."]
    except dns.resolver.NXDOMAIN:
        return ["Domain does not exist."]
    except rdatatype.UnknownRdatatype:
        return [f"Unknown record type: {record_type}"]
    except Exception as e:
        return [f"DNS query failed: {e}"]


class WhoisRecord(BaseModel):
    domain_name: str = Field(
        description="The fully qualified domain name (e.g., example.com)"
    )
    registrar: str = Field(
        description="The domain name registrar responsible for managing the domain"
    )
    whois_server: str = Field(
        description="The WHOIS server used to retrieve this record, if known"
    )
    updated_date: List[datetime] = Field(
        description="List of timestamps when the domain record was last updated"
    )
    creation_date: datetime = Field(
        description="The original date and time the domain was registered"
    )
    expiration_date: datetime = Field(
        description="The date and time the domain registration is set to expire"
    )
    name_servers: List[str] = Field(
        description="List of authoritative name servers for the domain"
    )
    status: List[str] = Field(
        description="List of domain status flags (e.g., clientTransferProhibited)"
    )
    emails: List[str] = Field(
        description="Email addresses associated with the registrant or contact; may be redacted"
    )
    dnssec: str = Field(
        description="Indicates whether DNSSEC is enabled (e.g., 'unsigned', 'signed')"
    )
    name: str = Field(description="The registrant's name (may be redacted for privacy)")
    org: str = Field(
        description="The registrant's organization or company (if provided)"
    )
    country: str = Field(
        description="Two-letter country code (ISO 3166) of the registrant"
    )


@tool
def get_domain_metadata(
    domain: Annotated[str, "The domain name to query (e.g., 'example.com')"],
) -> WhoisRecord:
    """
    Useful for retrieving general information about a domain name, such as its registrar, creation date, expiration date, and more.
    This function uses the `whois` library to fetch the WHOIS record for the specified domain.
    """
    w = whois(domain)
    emails = w.emails if isinstance(w.emails, list) else [w.emails] if w.emails else []

    return WhoisRecord(
        domain_name=w.domain_name or "",
        registrar=w.registrar or "",
        whois_server=w.whois_server or "",
        updated_date=w.updated_date,
        creation_date=w.creation_date,
        expiration_date=w.expiration_date,
        name_servers=w.name_servers,
        status=w.status,
        emails=emails,
        dnssec=w.dnssec or "",
        name=w.name or "",
        org=w.org or "",
        country=w.country or "",
    )
