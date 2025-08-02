# HOWTO: Troubleshoot Printer Network Issues

This guide helps you resolve connectivity issues with the **HP LaserJet Pro MFP 4103fdw Printer** using available documentation and network tools.

---

## ✅ Step-by-step Procedure

### 1. **Check Printer Power and Status**

- Ensure the printer is **powered on** and the display shows **Ready**.
- Refer to the \[HP LaserJet Pro MFP 4103fdw User Guide] for display error codes.

### 2. **Ping the Printer**

- Use the `ping` tool to check network reachability:

  ```
  ping <printer_IP_address>
  ```

  - ✅ If ping succeeds, printer is reachable.
  - ❌ If ping fails, proceed to Step 3.

### 3. **Check Switch Port Connection**

- **Identify the switch port** connected to the printer.

  ```
  gather switch port description
  ```

- **Check port status**:

  ```
  check port status <printer_port>
  ```

  - Look for `up/up` status.
  - ❌ If port is down, use:

    ```
    restart port <printer_port>
    ```

### 4. **Check Printer Network Settings**

- On the printer control panel:

  - Verify **IP address** (DHCP/static).
  - Check **network cable** connection.

### 5. **Consult Documentation**

- Reference:

  - _HP LaserJet Pro MFP 4103fdw User Guide_
  - _Troubleshooting procedure printer_
  - _Network diagram (written)_
