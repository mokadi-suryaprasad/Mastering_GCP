# SLI, SLO, SLA 

## ✅ What is an SLI (Service Level Indicator)?

**SLI = What we measure.**

It tells you **how your service is performing right now**.

### Example:

-   "Percentage of successful requests"
-   "Latency of API calls"
-   "Uptime of the service"

✅ **Real example:**\
Your API responds within **200 ms** for 98% of requests.\
This 98% is the **SLI**.

------------------------------------------------------------------------

## ✅ What is an SLO (Service Level Objective)?

**SLO = The target you want to achieve.**

It is a **goal or expectation** set by your engineering team.

### Example:

-   "Our API should respond within 200 ms for **99% of requests**."

✅ **Real example:**\
Your target is **99% success rate** → that is the **SLO**.

------------------------------------------------------------------------

## ✅ What is an SLA (Service Level Agreement)?

**SLA = A legal contract with customers.**

It includes: - Guaranteed performance\
- Penalties if you fail (refunds, credits)

### Example:

-   "We guarantee 99.5% uptime. If we fail, we give service credits."

✅ **Real example:**\
If your uptime drops below **99.5%**, customer gets 10% bill credit.\
This is the **SLA**.

------------------------------------------------------------------------

## ✅ Simple Comparison

  ------------------------------------------------------------------------
  Term              Meaning                   Example
  ----------------- ------------------------- ----------------------------
  **SLI**           What is happening now     98% success rate
                    (measurement)             

  **SLO**           What we aim for           Target = 99% success rate
                    (engineering target)      

  **SLA**           Promise to customers +    Guarantee = 99.5% uptime
                    penalty                   
  ------------------------------------------------------------------------

------------------------------------------------------------------------

## ✅ Real-Life Realtime Example (Very Easy)

Imagine you run a food delivery app:

-   **SLI:** How many orders are delivered on time?\
-   **SLO:** 95% orders must be delivered on time.\
-   **SLA:** If late delivery rate goes above 5%, customer gets
    coupon/refund.

------------------------------------------------------------------------

## ✅ One-Line Definitions

-   **SLI:** Actual performance.\
-   **SLO:** Expected performance.\
-   **SLA:** Promised performance with penalty.
