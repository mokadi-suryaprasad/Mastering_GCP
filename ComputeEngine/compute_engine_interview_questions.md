# Compute Engine Interview Questions (Very Clear & Simple)

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
