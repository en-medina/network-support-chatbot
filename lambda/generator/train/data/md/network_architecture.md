# Network Architecture

This document outlines the basic physical and logical connections within the office network setup. The focus is on how primary devices are interconnected to enable internal communication and external internet access.

## 1. Border Router → Main Switch

- The **Border Router** serves as the gateway between the internal office network and the external internet service provider (ISP).
- A **single Ethernet connection** links the Border Router to the **Main Switch**, allowing internal devices to access the internet and receive routing services (e.g., NAT, firewall rules).
- This connection is typically configured using a **Gigabit Ethernet** port to ensure sufficient bandwidth for all downstream devices.

## 2. Main Switch → Employees’ PCs

- The **Main Switch** connects to all **employees’ desktop or laptop computers** via individual Ethernet cables.
- Each **PC is assigned a dedicated switch port**, enabling full-duplex communication and providing internet access and internal network communication.
- Depending on the size of the team, this may utilize multiple switch ports or VLAN segmentation for better traffic management.

## 3. Main Switch → Employees’ VoIP Phones

- Each **VoIP phone** is also connected directly to the **Main Switch** via Ethernet.
- Phones can be powered using **Power over Ethernet (PoE)** ports if the switch supports it, eliminating the need for separate power adapters.
- VoIP traffic may be logically separated using a **dedicated VLAN** to ensure call quality and security.

## 4. Main Switch → Printer

- A shared **network printer** is connected to the **Main Switch** via Ethernet.
- This allows all employees to send print jobs over the local network.
- The printer is typically assigned a **static IP address** or reserved DHCP lease to maintain consistency.
