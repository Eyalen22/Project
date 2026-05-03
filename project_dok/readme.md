# DOKrypt - USB Device Management and Security

This project is designed for the secure management of files on USB devices. Below are the instructions for system configuration, execution, and client usage.

---

##  Path Configuration

Before running the project, you must update the local paths in the following files to ensure the system identifies the correct locations:

| File | Function | Location |
| :--- | :--- | :--- |
| `stand_logic.py` | `restore_to_dok` | Line 1 |
| `create_exe.py` | `run_full_process` | Line 1 |
| `server_logic.py` | `restore` | Line 3 |

---

##  Prerequisites

To successfully run the project, ensure the following requirements are met:

1. **Hardware:** A USB Flash Drive (Disk-on-Key) must be connected to the computer.
2. **Operating System:** A computer running Windows.
3. **File Organization:** Verify that all required files are located within their respective folders:
   - Server Folder
   - Installation Stand Folder
   - Client Folder

---

##  Execution Instructions

### 1. System Setup
To start the system, execute the following files:
* **Run the Server:** `SERVER_LOGIC.py`
* **Run the Installation Stand:** `STAND_LOGIC.py`

### 2. Client Execution (After Installation)
Once the installation process on the "Installation Stand" is complete:
1. Open your **USB Drive (DOK)**.
2. Locate the file named `OPENDOK`.
3. **Double-click** `OPENDOK` to run the client application.

---

> **Note:** Ensure the server is running and listening for connections before launching the stand or client logic.