from langchain_core.tools import tool
from netmiko import (
    ConnectHandler,
    NetmikoTimeoutException,
    NetmikoAuthenticationException,
)

import settings
from typing import Annotated, List


def get_connection_tools() -> List[tool]:
    """
    Returns a list of connection-related tools that can be used for diagnostics.
    Each tool is defined with its name, description, and function.
    """
    return [
        get_interfaces_status,
        get_interface_detail,
        # restart_interface,
        set_interface_shutdown,
    ]


def get_connection_tool_names() -> str:
    """
    Returns a comma-separated string of the names of all available connection tools.
    """
    return ", ".join([tool.name for tool in get_connection_tools()])


def evaluate_command_output(
    output: Annotated[str, "The raw CLI output returned from the Cisco device after running a command."]
) -> bool:
    """
    Evaluates a command's output for errors to determine if it executed successfully.

    Returns:
        bool: True if no Cisco CLI error messages were found in the output,
        otherwise False.
    """
    ERROR_MARKERS = [
        "% Invalid input",
        "% Incomplete command",
        "% Ambiguous command",
        "% Unrecognized command",
        "% Connection error",
        "% Unknown error",
    ]
    return not any(err in output for err in ERROR_MARKERS)


def get_device_profile(
    hostname: Annotated[str, "The logical device name or alias used to identify which Cisco device to connect to."]
) -> dict:
    """
    Retrieves the device connection profile (IP, port, credentials, and device type)
    for a given hostname. Uses configuration values from the settings module.

    Returns:
        dict: A dictionary containing Netmiko-compatible connection parameters.
    """
    # For demonstration purposes, we use localhost and default Telnet port.
    # In a real implementation, this would look up the device in a database or config.
    host = "127.0.0.1"
    port = 23
    if "main-router" in hostname.lower():
        host = settings.MAIN_ROUTER
        port = settings.MAIN_ROUTER_PORT
    device = {
        'device_type': 'cisco_ios_telnet',
        'host': host,
        'port': port,
        'username': '',
        'password': '',
    }
    return device


@tool
def get_interfaces_status(
    hostname: Annotated[str, "The hostname or alias of the Cisco device to query."]
) -> str:
    """
    Connects to a Cisco device and retrieves a summary of interface statuses.

    Equivalent to running: `show ip interface brief`.

    Returns:
        str: The raw command output from the device.
    """
    device = get_device_profile(hostname)

    try:
        with ConnectHandler(**device) as net_connect:
            net_connect.enable()
            output = net_connect.send_command("show ip interface brief")
    except Exception as e:
        output = f"% Connection error with {hostname}: {e}"
    return output


@tool
def get_interface_detail(
    hostname: Annotated[str, "The hostname or alias of the Cisco device."],
    interface: Annotated[str, "The interface identifier (e.g., 'GigabitEthernet0/1')."]
) -> str:
    """
    Retrieves detailed information about a specific interface on a Cisco device.

    Equivalent to running: `show interface <interface>`.

    Returns:
        str: The raw command output containing detailed interface information.
    """
    device = get_device_profile(hostname)

    try:
        with ConnectHandler(**device) as net_connect:
            net_connect.enable()
            command = f"show interface {interface}"
            output = net_connect.send_command(command)
    except Exception as e:
        output = f"% Connection error with {hostname}: {e}"
    return output


@tool
def restart_interface(
    hostname: Annotated[str, "The hostname or alias of the Cisco device."],
    interface: Annotated[str, "The name of the interface to restart (e.g., 'GigabitEthernet0/1')."]
) -> bool:
    """
    Performs a soft restart on a specific Cisco interface by issuing
    'shutdown' followed by 'no shutdown' commands.

    Returns:
        bool: True if the commands executed successfully, otherwise False.
    """
    device = get_device_profile(hostname)

    try:
        with ConnectHandler(**device) as net_connect:
            net_connect.enable()
            commands = [f"interface {interface}", "shutdown", "no shutdown"]
            output = net_connect.send_config_set(commands)
    except Exception as e:
        output = f"% Connection error with {hostname}: {e}"
    return evaluate_command_output(output)


@tool
def set_interface_shutdown(
    hostname: Annotated[str, "The hostname or alias of the Cisco device."],
    interface: Annotated[str, "The name of the interface to configure."],
    shutdown: Annotated[bool, "Whether to shut down (True) or enable (False) the interface."]
) -> bool:
    """
    Configures a Cisco interface's administrative state (shutdown or no shutdown).

    Args:
        hostname (str): The device hostname or alias.
        interface (str): The interface identifier.
        shutdown (bool): True to shut down the interface, False to enable it.

    Returns:
        bool: True if the configuration was applied successfully, otherwise False.
    """
    device = get_device_profile(hostname)

    try:
        with ConnectHandler(**device) as net_connect:
            net_connect.enable()
            commands = [f"interface {interface}"]
            commands.append("shutdown" if shutdown else "no shutdown")
            output = net_connect.send_config_set(commands)
    except Exception as e:
        output = f"% Connection error with {hostname}: {e}"
    return evaluate_command_output(output)
