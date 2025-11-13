# Compute Engine Interview Questions

This document contains simple and clear explanations of Google Cloud Compute Engine concepts. Use this for interviews.

---

## 1. What is Compute Engine?
Compute Engine is a service in Google Cloud that gives you **Virtual Machines (VMs)**.  
These VMs are like computers running in the **cloud**, not in your office.

---

## 2. Why do we use Compute Engine?
We use Compute Engine when we need:
- Full control over the operating system
- To install any software
- To run applications that need servers

It works like a normal computer, but we manage it online.

---

## 3. Difference between Compute Engine and App Engine
| Compute Engine | App Engine |
|----------------|-----------|
| Gives full VM/server access | Only deploy your code |
| You manage OS, patches, scaling | Google manages everything |
| More control, more work | Less control, easy to use |

---

## 4. What is a Preemptible VM?
A **Preemptible VM** is a **low-cost VM**.  
Google can **stop** it anytime (maximum running time is **24 hours**).  
Use it for **testing or short jobs**, not for important applications.

---

## 5. What is a Persistent Disk?
Persistent Disk is **storage attached to the VM**.  
Your data remains **safe even when the VM is stopped or restarted**.

---

## 6. Difference Between Persistent Disk and Local SSD
| Persistent Disk | Local SSD |
|-----------------|----------|
| Data remains safe | Data gets deleted if VM stops |
| Slower | Very fast |
| Good for normal use | Good for high-speed processing |

---

## 7. What is an Instance Template?
Instance Template is a **saved VM configuration**.  
Instead of creating VMs manually every time, we use the template to **create multiple VMs quickly and consistently**.

---

## 8. What is a Managed Instance Group (MIG)?
A MIG is a **group of VMs** created using an instance template.  
It can:
- **Auto-scale** (increase/decrease VM count)
- **Auto-heal** (replace failed VMs)
- Work behind **Load Balancer**

Example: If one VM crashes, MIG creates a new one automatically.

---

## 9. What is Auto-scaling?
Auto-scaling means **VMs are added or removed automatically** based on load.  
If traffic increases → more VMs.  
If traffic decreases → fewer VMs.

This saves **cost**.

---

## 10. What is a Service Account on VM?
A **Service Account** allows a VM to **securely access** Google Cloud services (Example: Storage, BigQuery).  
It works like a **identity with permissions**.

---

## 11. Internal IP vs External IP
- **Internal IP**: Used **inside** the VPC network. Other VMs can reach it.
- **External IP**: Used to access VM **from internet**.

---

## 12. How to allow HTTP/HTTPS traffic to a VM?
We must create **Firewall Rules** to allow:
- Port **80** → HTTP
- Port **443** → HTTPS

Or check **"Allow HTTP/HTTPS"** while creating the VM.

---

## 13. What is Live Migration?
Google moves your **running VM** to another physical machine **without shutting it down**.  
This keeps applications running during maintenance.

---

## 14. How to make an application Highly Available?
Use:
1. **Managed Instance Group**
2. **Load Balancer**
3. **Multiple Zones**

If one zone fails, applications still work.

---

## 15. Cost Saving Tips
- Use **Preemptible VMs** for testing or batch jobs
- Use **Auto-scaling**
- Choose correct **machine type**
- Stop VMs when not in use

---

## Summary
Compute Engine gives flexible VMs where you control software and configuration.  
High availability is achieved through **Managed Instance Groups** and **Load Balancers**.  
Costs can be reduced using **Preemptible VMs** and **Auto-scaling**.

---

End of Document.


## Scenario-Based Questions & Answers

## Accessing Google Compute Engine (GCE) VM Using Only Private IP

When a VM has **no public IP**, you cannot SSH directly from the internet.  
Below are the **important and secure methods** to access a private-only VM.

---

## 1. Cloud IAP (Identity-Aware Proxy) — ⭐ Most Recommended

Cloud IAP lets you SSH into VMs **without a public IP** using a secure Google-managed tunnel.

### Command
```bash
gcloud compute ssh <vm-name> --zone <zone> --tunnel-through-iap
```

### Requirements
- Enable **IAP API**
- IAM Role: `IAP-Secured Tunnel User`
- Firewall rule allowing:
  ```
  Source: 35.235.240.0/20
  Port: tcp:22
  ```

### Why Use It?
- Most secure  
- No need for bastion  
- Identity-based access  

---

## 2. Bastion Host (Jump Host)

A bastion host is a **public VM** used to access private VMs inside the VPC.

### Steps
1. Create a bastion VM with a public IP.
2. SSH into the bastion:
```bash
ssh <user>@<bastion-public-ip>
```
3. From bastion → SSH into private VM:
```bash
ssh <user>@<private-ip>
```

### Notes
- Restrict bastion access to your IP.
- Use OS Login or SSH keys.

---

## 3. Cloud Shell SSH (Internal Google Network)

Google Cloud Shell has internal access to your VPC.

### Command
```bash
gcloud compute ssh <vm-name> --zone <zone>
```

### Requirements
- IAM: Compute OS Login roles  
- Firewall rule allowing SSH (tcp/22) from internal ranges  
- No public IP needed  

---

## 4. VPN / Interconnect / VPC Peering

If your local network is connected to the VPC, you can directly SSH using the private IP.

### After VPN/Peering/Interconnect setup:
```bash
ssh <user>@<private-ip>
```

### Required Firewall
```
Port: tcp:22
Source: on-prem CIDR
```

### Best For
- Enterprise on-prem access  
- Secure hybrid environments  

---

## 5. Serial Console (Emergency Access Only)

When SSH is broken, use the serial console.

### Enable Serial Port
```bash
gcloud compute instances add-metadata <vm-name> \
  --metadata=serial-port-enable=1
```

### Connect
```bash
gcloud compute connect-to-serial-port <vm-name>
```

### Notes
- Not SSH  
- Use only for troubleshooting  

---

# Summary Table

| Method | Needs Public IP? | Security | Best Use Case |
|--------|------------------|----------|----------------|
| **IAP SSH** | ❌ No | ⭐⭐⭐⭐⭐ | Enterprise, Production |
| **Bastion Host** | ✔ Bastion only | ⭐⭐⭐⭐ | Traditional env |
| **Cloud Shell** | ❌ No | ⭐⭐⭐⭐ | Quick access |
| **VPN/Interconnect** | ❌ No | ⭐⭐⭐⭐ | On-prem integration |
| **Serial Console** | ❌ No | ⭐⭐⭐ | Fix SSH issues |

---

# Recommended Method
**Use Cloud IAP SSH** — secure, modern, no public IP required.

