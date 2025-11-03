# ✅ Google Cloud DNS --- Complete Beginner to Advanced Guide

Google Cloud DNS is a **high‑performance, scalable, global Domain Name
System (DNS) service** hosted on Google Cloud.

It helps map: - **Domain → IP Address** - **Service name → Load
balancer** - **Subdomain → VM / GKE Service / Cloud Run**

------------------------------------------------------------------------

# ✅ 1. What is Cloud DNS?

Cloud DNS is a **managed DNS service** that provides: - Fast DNS lookups
(Google Edge Network) - High availability (global anycast) - Low
latency - DNSSEC support - Private DNS zones for internal GCP networks

✅ **Simple Definition:**\
Cloud DNS allows you to manage your domain names and route traffic to
your services.

------------------------------------------------------------------------

# ✅ 2. Types of DNS Zones

### **1. Public Zone**

Used for domains accessible on the internet.\
Example:\
`example.com → Load Balancer IP`

### **2. Private Zone**

Used inside a VPC network (internal services).\
Example:\
`redis.internal → 10.0.0.5`

### **3. Forwarding Zone**

Sends DNS queries to a specific DNS server.\
Used for hybrid networks (VPN / Interconnect).

### **4. Peering Zone**

Allows one VPC to use DNS from another VPC.

✅ **Simple Example:**\
Your GKE cluster in VPC A can resolve names inside VPC B.

------------------------------------------------------------------------

# ✅ 3. Common DNS Record Types


  Record      Purpose                   Example
  ----------- ------------------------- -----------------------------------
  **A**       Domain → IPv4             `example.com → 34.12.56.8`
  **AAAA**    Domain → IPv6             `example.com → ::1`
  **CNAME**   Alias to another domain   `www → example.com`
  **MX**      Email server              `example.com → mail server`
  **TXT**     Verification, SPF         `"google-site-verification=xxxx"`
  **NS**      Nameserver records        Delegates DNS authority
  **SRV**     Service records           `sip`, `ldap`, etc.

------------------------------------------------------------------------

# ✅ 4. How to Create a Public DNS Zone (Step-by-step)

### ✅ Step 1 --- Open Cloud DNS

Google Console → **Network Services → Cloud DNS**

### ✅ Step 2 --- Create Zone

-   Click **Create Zone**
-   Zone Type: **Public**
-   Zone Name: `my-public-zone`
-   DNS Name: `example.com.`

### ✅ Step 3 --- Add DNS Records

Example A record:

    Name: @
    Type: A
    TTL: 300
    IPv4 Address: 34.118.22.10

Example CNAME:

    Name: www
    Type: CNAME
    Alias: example.com.

### ✅ Step 4 --- Update Domain Registrar

Your domain provider will ask for **nameservers**.

Use Google NS records:

    ns-cloud-a1.googledomains.com
    ns-cloud-a2.googledomains.com
    ns-cloud-a3.googledomains.com
    ns-cloud-a4.googledomains.com

✅ After propagation (5 mins to 48 hrs), your website works globally.

------------------------------------------------------------------------

# ✅ 5. Create a Private DNS Zone (Internal DNS)

Used inside your VPC.

### Example

Create zone:

    internal-zone
    DNS name: internal.
    Type: Private

Attach VPC:

    vpc-production

Add A record:

    db.internal → 10.10.0.6

✅ Now any VM/GKE pod in the VPC can resolve `db.internal`.

------------------------------------------------------------------------

# ✅ 6. DNS with GKE (Kubernetes)

GKE automatically integrates with Cloud DNS using: - **Cloud DNS for
service discovery** - **Autopilot load balancers** - **ExternalDNS
(optional)**

Example ExternalDNS annotation:

``` yaml
metadata:
  annotations:
    external-dns.alpha.kubernetes.io/hostname: app.example.com
```

------------------------------------------------------------------------

# ✅ 7. DNS for Global Load Balancer

### Step 1 --- Get Load Balancer IP

Example:

    34.118.20.4

### Step 2 --- Create A Record in Cloud DNS

    app.example.com → 34.118.20.4

✅ Traffic globally reaches your load balancer.

------------------------------------------------------------------------

# ✅ 8. DNSSEC (Optional)

Cloud DNS supports DNSSEC which: - Prevents DNS spoofing - Adds
cryptographic signatures

Enable from Cloud DNS → Zone Settings → DNSSEC → Enable.

------------------------------------------------------------------------

# ✅ 9. Troubleshooting

### ✅ Check DNS resolution

    nslookup example.com

### ✅ Check if Public DNS is responding

    dig example.com @8.8.8.8

### ✅ Check propagation

Use online tools like: - whatsmydns.net

### ✅ Common Issues

  Issue                           Reason
  ------------------------------- ----------------------------------
  Website not loading             NS records not updated
  DNS propagation slow            TTL too high
  Internal domain not resolving   VPC not attached to private zone
  Wrong LB IP                     A record incorrect

------------------------------------------------------------------------

# ✅ 10. Real-Time Example: GKE + Cloud DNS

You deploy a GKE app and expose via load balancer:

1.  GKE gives LoadBalancer IP:

        35.201.22.17

2.  You create DNS record:

        api.myapp.com → 35.201.22.17

3.  Now users access the GKE app globally using the domain.

✅ This is the **most common production use case.**

------------------------------------------------------------------------

# ✅ 11. Interview Questions

### **1. What is Cloud DNS?**

A global, scalable DNS service for mapping domain names to IP addresses.

### **2. What is a Public Zone?**

A DNS zone accessible on the internet.

### **3. What is a Private Zone?**

DNS zone accessible only inside a VPC.

### **4. What is the difference between A and CNAME records?**

-   A record → maps domain → IP\
-   CNAME → maps domain → another domain

### **5. What is DNS Peering?**

Allow VPC A to resolve DNS of VPC B.

### **6. What tools check DNS?**

`nslookup`, `dig`, Cloud DNS logs.

------------------------------------------------------------------------

