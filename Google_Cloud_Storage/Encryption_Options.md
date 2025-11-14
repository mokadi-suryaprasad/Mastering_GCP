# 🔐 Encryption Options in Google Cloud

Google Cloud always encrypts your data at rest.  
You get two choices for how your data is encrypted:

1. **Google-managed encryption keys (default)**  
2. **Customer-managed encryption keys (CMEK) using Cloud KMS**

Below is the easiest explanation of how both options work, with real examples.

---

# 🟩 1. Google-Managed Encryption Keys (Default)

## ✔️ How It Works
- You upload data to Cloud Storage  
- Google automatically encrypts it  
- Google stores and protects the encryption key  
- Google rotates the key regularly  
- You only read/write files — no key work needed

## 🎯 Simple Understanding
> **Google keeps the locker and the key. You just store your files in the locker.**

## 📌 Real Example
You upload:
```
salary-report-2025.pdf
```
into:
```
gs://payroll-team-bucket
```
Google encrypts it automatically using Google-managed keys.

## 🖥️ Console View
Go to:
- Bucket → **Settings → Encryption**
- You will see: **Google-managed keys**

---

# 🟦 2. Customer-Managed Encryption Keys (CMEK)

## ✔️ How It Works (Easy English)
- You create your own key in Cloud KMS  
- You allow Cloud Storage to use this key  
- You attach the key to your bucket  
- All new files are encrypted with *your* key  
- If you disable the key → nobody can read the files (not even Google)

## 🎯 Simple Understanding
> **Google gives you the locker, but *you* keep the key. If you hide the key, nobody can open the locker.**

## 📌 Real Example
Create a KMS key:
```
payroll-cmek-key
```
in:
```
Key Ring: payroll-keyring
Location: asia-south1
```

Attach it to:
```
gs://payroll-team-bucket
```

Now:
- All payroll files use this CMEK key  
- Disabling the key makes data unreadable  
- You get full audit logs showing who used the key

## 🖥️ Console Steps
1. Go to **Security → KMS**  
2. Create KeyRing → Create Key  
3. Give Storage service account **CryptoKey Encrypter/Decrypter**  
4. Go to bucket → **Settings → Encryption**  
5. Select **Customer-managed key (CMEK)**  
6. Choose `payroll-cmek-key`  

---

# 🏁 Comparison Table

| Feature | Google-Managed Keys | CMEK |
|--------|----------------------|------|
| Key Owner | Google | You |
| Setup Required | None | Yes |
| Best For | Regular workloads | Sensitive (Payroll, HR, Finance) |
| Key Rotation | Automatic | You decide |
| If Key Disabled | Not needed | Data becomes unreadable |
| Audit Logs | Limited | Full key usage logs |

---

# 🎉 One-Line Summary

### Google-managed keys:
> **Google keeps the key — easiest and automatic.**

### CMEK:
> **You keep the key — most secure and fully controlled.**

