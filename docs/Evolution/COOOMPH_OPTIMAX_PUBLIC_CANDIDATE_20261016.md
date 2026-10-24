# CoOomph OptiMax+ Public Candidate

**Status:** PUBLIC CANDIDATE / REVIEWABLE / NOT MERGED

## Thesis

Treat resource allocation as a continuously evolving search problem. Explore a very large logical space of possible allocations and instantiate only the useful subset supported by current capacity and evidence.

## Search dimensions

- workload and dependency graph
- parallel width
- worker role
- model/provider diversity
- device/substrate
- time and scheduling window
- verification capacity
- recovery capacity
- energy and storage
- human attention
- audience/receiver needs

## Candidate allocation families

serial baseline

fixed-width parallel

adaptive parallel with backpressure

heterogeneous tripie/quadpie/multipie

production plus independent challenge

production plus recovery reserve

exploration plus production

provider-diverse routing

locality-aware routing

temporal checkpointing

mixed-objective allocation

## Large-scale virtual testing

Limitless physical execution is neither required nor claimed. Very large logical candidate populations can be simulated or sampled using:

- hierarchical search
- randomized sampling
- adversarial testing
- counterfactual replay
- adaptive refinement
- Pareto-frontier analysis

The purpose is to discover allocation regimes, bottlenecks, diminishing returns, threshold effects, and failure modes before spending substantial physical resources.

## Measures

throughput

latency

queue age

useful-work ratio

verification rate

error rate

recovery time

resource utilization

energy per useful result

optionality preserved

common-mode exposure

human intervention count

receiver propagation rate

## Multipie hypothesis

Multiplicity may create value beyond simple replication.

A tripie candidate can combine:

EXECUTE + CHALLENGE + RECOVER

A quadpie candidate can add:

EXPLORE

Roles may rotate among verification, routing, observation, forecasting, perturbation, and compression.

The hypothesis is testable:

**multiplicity -> new relations -> new capabilities**

It should not be assumed true without measurements.

## Sustainability

At scale, semantic persistence can be separated from continuous execution.

Useful states may be:

active

warm

cold

shadow

dormant

rehydratable

This can preserve identity, provenance, currentness, and recovery potential while reducing unnecessary continuous resource consumption.

## Optimization principle

A candidate allocation is better when it produces a meaningful positive net delta across the intended objective set without unacceptable increases in risk, fragility, coordination cost, resource use, or human burden.

**NEW != BETTER**

**MORE != BETTER**

**SPEED != USEFULNESS**

**SIMULATION != PRODUCTION PROOF**

**VIRTUAL SCALE != PHYSICAL CAPACITY**

## Public boundary

This document is a public-safe research candidate. It does not claim that an OptiMax solution has been discovered, that unlimited resources exist, or that any runtime automation or external effect is active.

