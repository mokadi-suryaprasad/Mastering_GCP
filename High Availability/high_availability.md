# High Availability & Cloud Deployment Strategies

> Deep-dive: 5 cloud deployment strategies, Netflix case study (Netflix vs AWS outage), Chaos Engineering, No-Trust architecture, and how top companies achieve 99.999% availability.

---

## Contents

1. Executive summary
2. The 5 cloud deployment strategies — definitions, when to use, pros & cons
3. Key reliability patterns and primitives
4. Netflix case study: how design-for-failure and Chaos Engineering kept Netflix running during AWS outages
5. Active-Active Independent vs other strategies — realistic trade-offs
6. No Trust Architecture (what it means and how to implement)
7. Practical checklist & runbook for designing 99.999% availability
8. Further reading & next steps

---

## 1. Executive summary

High availability (HA) is a set of design goals and operational practices that maximise service uptime despite failures in software, hardware, networks, or entire cloud regions. The goal of 99.999% (five nines) availability allows roughly ~5.26 minutes of downtime per year — a very aggressive objective that requires fault-tolerant design, redundancy at multiple levels, and disciplined operations (monitoring, runbooks, drills).

This document explains five common deployment strategies, core HA patterns, and a practical case study on Netflix’s approach to building reliable services under cloud failures.

---

## 2. The 5 cloud deployment strategies

### 1) Single Region, Single AZ

**Description:** All resources run in one cloud region and one availability zone.

**When to use:** Proof-of-concept, dev/test, or non-critical workloads with very low cost tolerance.

**Pros:** Cheapest, simplest, lowest operational overhead.
**Cons:** Single point of failure (region or AZ outage → total outage).

**Failure modes to plan for:** host failures, AZ-wide networking/storage issues.

---

### 2) Single Region, Multi-AZ

**Description:** Use multiple availability zones inside a single region for redundancy.

**When to use:** Production services that need resilience to AZ failure but can tolerate region-level risk.

**Pros:** Better resilience to AZ outage, relatively simple cross-AZ networking and replication.
**Cons:** Region-level outage still catastrophic; cross-AZ replication can add latency/cost.

**Important patterns:** multi-AZ load balancing, cross-AZ database replication (synchronous or semi-sync depending on RTO/RPO), sticky session avoidance or session replication.

---

### 3) Active-Passive Region (Warm Standby)

**Description:** A primary region runs actively; a secondary region holds a less-active standby (replicated data, autoscaling templates) that can be failed over after detection.

**When to use:** When cost constraints prevent full active-active but business needs a disaster recovery plan with reasonably quick failover.

**Pros:** Lower cost than fully active-active, deterministic failover process.
**Cons:** RTO and RPO depend on replication and promotion speed; failover complexity and DNS/clients caches cause delays.

**Key considerations:** automation for failover, database promotion strategy, regular failover drills, careful handling of external dependencies.

---

### 4) Active-Active Region

**Description:** Two (or more) regions actively serve traffic and keep data synchronized (either via strong replication or eventual-consistency models). Traffic can be load-balanced globally.

**When to use:** Services that must remain available even if a whole region fails and can handle multi-region consistency trade-offs.

**Pros:** Fast recovery from region failure, can distribute load geographically for latency benefits.
**Cons:** Complex data consistency, multi-region latency, cost higher, operational complexity for deployment and testing.

**Patterns:** global load-balancing (DNS + anycast + GSLB), conflict resolution strategies (CRDTs, vector clocks), multi-master vs primary-secondary replication choices.

---

### 5) Active-Active Independent (Independent Cloud / Multi-Cloud Active-Active)

**Description:** Application runs actively across independent clouds or providers (e.g., AWS + GCP or AWS + on-prem), avoiding vendor-specific single points. Each cloud is treated as an independent availability domain.

**When to use:** Organizations with strict regulatory, vendor-risk, or extreme availability requirements, and the budget and engineering capability to maintain multiple cloud stacks.

**Pros:** Highest resilience to vendor-wide failures, no single-cloud dependency, potential to leverage best-of-breed services from each vendor.
**Cons:** Very high complexity — networking, identity, observability, deployment pipelines, data replication, and cost. Not a silver bullet; will increase operational burden.

**Reality check:** Very few companies fully run core user-facing traffic actively across multiple providers at massive scale because of data-layer complexities and engineering cost. More common patterns are: multi-region within a single cloud plus using a second cloud for non-critical workloads (analytics, backups), or using cross-cloud tools (Spinnaker, Terraform) to reduce vendor lock-in.

---

## 3. Key reliability patterns and primitives

* **Redundancy & diversity:** Multiple instances, AZs, regions, and sometimes providers.
* **Health checks & graceful degradation:** Circuit breakers, bulkheads, rate limits, and degraded feature sets.
* **Observability & SLOs:** Metrics, tracing, logs, alerting, and clear SLO/SLI definitions.
* **Traffic steering & global load balancing:** DNS strategies (low TTL), geo-load balancing, anycast, and GSLB.
* **Data replication & consistency models:** asynchronous replication, multi-master, conflict-resolution.
* **Immutability & auto-replacement:** Pets → cattle, fast replacement and auto-healing.
* **Chaos engineering & drills:** automated fault injection, game days, and post-mortems.
* **Runbooks & automation:** Scripted recoveries, codified runbooks, and operator training.

---

## 4. Netflix case study: design-for-failure, Chaos Engineering, and AWS outages

**Short history & context**
Netflix migrated from on-prem to AWS early and relies heavily on AWS for compute, storage and core services. In the early 2010s, AWS experienced outages that affected many customers. Netflix used those events as learning opportunities to build resilience at the application layer rather than rely on a single heroic cloud fix.

**Core approaches Netflix used**

* **Design for failure:** Accept that components (instances, AZs, services) will fail and design services to handle transient and permanent failures.
* **Simian Army & Chaos Monkey:** Netflix open-sourced the Simian Army suite (Chaos Monkey, Latency Monkey, Conformity Monkey, etc.) to randomly terminate instances and inject failures to test real-world resilience.
* **Service isolation & bulkheads:** Microservices isolate failure domains so one service's failure doesn't cascade.
* **Fallbacks & graceful degradation:** If a non-critical capability fails (recommendations, personalization), Netflix degrades gracefully (serve video without extra features) rather than failing the whole playback experience.
* **Automated recovery:** Auto-scaling groups, health checks and automated redeployments speed recovery.
* **Spinnaker & deployment fitness:** Spinnaker helped manage complex multi-region deployment and rollout strategies (blue-green/red-black), enabling safer rollouts and quick rollbacks.

**Why Netflix stayed up during notable AWS outages**
By intentionally exercising failures and building application-level resilience (fallback logic, retries, timeouts, degraded modes), Netflix could keep the most critical path — video playback — running even when supporting systems or parts of the cloud experienced trouble. This is the classic "design for failure" lesson: application-level resilience trumps assuming the cloud will always be available.

**Important nuance**
Although Netflix engineered independence from region or instance failures, it historically runs most production workloads on AWS. Netflix used multi-region strategies, strong automation, and chaos engineering rather than fully splitting traffic across multiple cloud providers for its primary streaming service. Tools like Spinnaker and open-source contributions facilitated multi-cloud capabilities if needed, but Netflix’s practical posture focused on making its systems resilient inside and across AWS regions and AZs while leveraging Netflix’s own correctness and resilience patterns.

---

## 5. Active-Active Independent vs other strategies — trade-offs & when to choose

**Trade-offs summary**

* **Cost:** multi-cloud active-active is the most expensive (duplicate resources, cross-cloud egress, cross-region storage). A warm-standby or multi-AZ approach is cheaper.
* **Complexity:** multi-cloud adds complexity in identity, networking, CI/CD, and incident response. Plan for cross-domain failure modes and longer root-cause analysis.
* **Data & consistency:** synchronising state across clouds is the hardest part. Many architectures move state into a single authoritative store or favour eventual consistency.
* **Time-to-recover vs time-to-detect:** Active-active reduces recovery time but forces you to manage consistency. Active-passive increases detection and failover time.

**Decision heuristics**

* If your business requires continuous uptime across vendor outages (financial markets, core telecommunications), invest in multi-cloud active-active — but only if you have the engineering capability and clear SLOs.
* For most internet-scale consumer services, multi-region within a primary cloud plus robust chaos engineering and automated failover delivers strong availability at lower cost.

---

## 6. No Trust Architecture (what it means & how to implement)

**Definition:** In this context, a No Trust Architecture means an operational posture that assumes external systems (including cloud provider services) can fail unexpectedly. Instead of trusting an infra layer to never fail, designers build redundancy, checks, and isolation beyond the provider guarantees.

**Principles:**

* Assume components fail frequently.
* Push logic for retries, fallback, and rate limiting into the application.
* Validate all interactions (timeouts, circuit breakers).
* Prefer idempotent operations for retries.
* Keep least-privilege identity and ephemeral credentials; design recovery without long-lived manual secrets.

**Implementation checklist:**

* Instrument SLIs and SLOs per service path.
* Use circuit breakers and timeouts at external calls.
* Provide graceful degradation feature flags to reduce functionality automatically when upstream fails.
* Maintain independent backup and restore strategies (cross-region snapshots, snapshots exported to external storage).
* Automate failovers and test them regularly with game days.

---

## 7. Practical checklist & runbook for designing 99.999% availability

### Architectural checklist

* Multi-AZ deployments for every critical service.
* Global traffic management (low-TTL DNS, GSLB/anycast) when multi-region.
* Stateless frontends, stateful stores with cross-region replication patterns documented.
* Automated health checks with fast replacement.
* Circuit breakers + exponential backoff + idempotency.
* Observability: distributed tracing, high-cardinality metrics, alerting on SLO breaches.

### Operational checklist

* Weekly smoke tests, monthly failover drills, quarterly full-region exercises.
* Chaos engineering schedule: run non-disruptive tests in canaries; escalate to production after confidence.
* Incident response runbooks for region failover, database promotion, DNS switchover.
* Post-mortem culture + corrective action tracking.

### Example runbook snippet (region failover)

1. Confirm region outage via provider status and internal telemetry.
2. Trigger traffic reweighting from Region-A to Region-B using GSLB or CDN control plane.
3. Promote or switch database read/write endpoints if required (only for systems designed for promotion).
4. Validate functional smoke tests (playback flows / critical transactions).
5. Monitor error rates and SLOs; roll back routing if errors exceed thresholds.
6. Post-mortem and RCA within 72 hours.

---


## 9. Further reading & next steps

* Start with defining SLIs and SLOs for your critical user journeys.
* Build a small chaos-engineering pipeline for non-prod; make sure to have quick rollbacks.
* If considering multi-cloud active-active, prototype a single stateless service across multiple providers first and validate CI/CD, telemetry and failover workflows.

---
