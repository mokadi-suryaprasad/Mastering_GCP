# Cloud_Dns.md

## ✅ Google Cloud DNS — Complete Beginner to Advanced Guide

Google Cloud DNS is a **high‑performance, scalable, global Domain Name System (DNS) service** on Google Cloud.

It maps:
- Domain → IP Address  
- Service name → Load Balancer  
- Subdomain → VM / GKE / Cloud Run  

---

## ✅ 1. What is Cloud DNS?

Cloud DNS is a **managed DNS service** that gives:
- Very fast DNS lookups (Google Edge Network)
- High availability (global anycast)
- Low latency
- DNSSEC support
- **Private DNS** for internal resources

✅ **Simple Definition:**  
Cloud DNS helps you manage domain names and route traffic to your services.

---

## ✅ 2. Types of DNS Zones

### ✅ 1. Public Zone
Accessible on the **internet**.

Example:  
`example.com → Load Balancer IP`

### ✅ 2. Private Zone
Used **inside VPC** (internal).

Example:  
`db.internal → 10.0.0.5`

### ✅ 3. Forwarding Zone
Forward DNS queries to on‑prem DNS servers.

Used in **hybrid networks** (VPN / Interconnect).

### ✅ 4. Peering Zone
Allow DNS resolution between 2 VPCs.

Example:  
VPC-A services can resolve names in VPC-B.

---

## ✅ 3. Common DNS Record Types

| Record | Purpose | Example |
|-------|---------|---------|
| **A** | Domain → IPv4 | `example.com → 34.12.56.8` |
| **AAAA** | Domain → IPv6 | `example.com → ::1` |
| **CNAME** | Alias | `www → example.com` |
| **MX** | Email servers | Gmail routing |
| **TXT** | Verifications, SPF | `"google-site-verification=xxx"` |
| **NS** | Delegates DNS authority | List of nameservers |
| **SRV** | Service records | SIP, LDAP |

---

## ✅ 4. Create a Public DNS Zone (Step-by-step)

### ✅ Step 1 — Open Cloud DNS  
**Google Console → Network Services → Cloud DNS**

### ✅ Step 2 — Create Zone
- Zone Type: **Public**
- Zone Name: `my-public-zone`
- DNS Name: `example.com.`

### ✅ Step 3 — Add DNS Records

A record:
```
Name: @
Type: A
TTL: 300
IPv4: 34.118.22.10
```

CNAME:
```
Name: www
Type: CNAME
Target: example.com.
```

### ✅ Step 4 — Update Domain Registrar  
Use these Google nameservers:

```
ns-cloud-a1.googledomains.com
ns-cloud-a2.googledomains.com
ns-cloud-a3.googledomains.com
ns-cloud-a4.googledomains.com
```

---

## ✅ 5. Create a Private DNS Zone (Internal DNS)

Example:

```
Zone Name: internal-zone
DNS Name: internal.
Type: Private
Attached VPC: vpc-production
```

Create A record:

```
db.internal → 10.10.0.6
```

✅ All VMs and GKE pods in the VPC can resolve `db.internal`.

---

## ✅ 6. DNS with GKE (Kubernetes)

GKE integrates automatically with Cloud DNS.

ExternalDNS example:

```yaml
metadata:
  annotations:
    external-dns.alpha.kubernetes.io/hostname: app.example.com
```

✅ Auto-creates DNS records for Kubernetes services.

---

## ✅ 7. DNS for Global Load Balancer

Get LB IP:
```
34.118.20.4
```

Create A record:
```
app.example.com → 34.118.20.4
```

✅ Global users reach your app via domain.

---

## ✅ 8. DNSSEC (Optional Security)

DNSSEC:
- Prevents DNS spoofing  
- Adds cryptographic signatures  

Enable: **Cloud DNS → Zone Settings → DNSSEC ON**

---

## ✅ 9. Troubleshooting

### ✅ Check DNS Resolution
```
nslookup example.com
```

### ✅ Use Google's DNS
```
dig example.com @8.8.8.8
```

### ✅ Common Problems & Fixes

| Issue | Cause |
|-------|-------|
| Website not loading | Nameservers not updated |
| DNS propagation slow | TTL is high |
| Internal names not resolving | VPC not attached to private zone |
| Wrong destination | Incorrect A record |

---

## ✅ 10. Real-Time Example: GKE + Cloud DNS

1. Deploy GKE app → Get LoadBalancer IP:
```
35.201.22.17
```

2. Create DNS record:
```
api.myapp.com → 35.201.22.17
```

✅ Users can now access your app globally.

---

## ✅ 11. Interview Questions

### ✅ 1. What is Cloud DNS?
A global DNS service for mapping domain names to IP addresses.

### ✅ 2. What is a Public Zone?
DNS zone accessible on the **internet**.

### ✅ 3. What is a Private Zone?
DNS zone that works **only inside a VPC**.

### ✅ 4. Difference between A and CNAME?
- A → domain to IP  
- CNAME → domain to another domain  

### ✅ 5. What is DNS Peering?
Allows one VPC to use DNS records of another VPC.

### ✅ 6. How to check DNS?
Use:
```
dig
nslookup
```

---
