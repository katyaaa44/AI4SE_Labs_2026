# RentYourExpert Architecture Discussion Notes

## 2026-10-28 — Initial project review

- Read the RentYourExpert requirements from the `/data` folder.
- Identified the main actors: Customer, Worker, and Administrator.
- Summarized the main functionality:
  - registration and login,
  - profiles,
  - worker search by skill and location,
  - service requests,
  - reviews,
  - Q&A,
  - administration.
- Identified important architectural concerns: authorization, request consistency, search, data ownership, moderation, and maintainability.
- Noted that the requirements do not define technology stack, hosting, scale, budget, or team size.

## 2026-10-28 — Three architecture options

- Proposed three different architectures for RentYourExpert:
  1. Layered modular monolith.
  2. Domain-oriented microservices.
  3. Serverless event-driven architecture.
- Started with a short overview before discussing the architectures in more detail.

## 2026-10-28 — Modular monolith discussion

- Discussed a layered modular monolith with modules such as:
  - Identity,
  - Profiles/Catalogue,
  - Requests,
  - Reviews,
  - Q&A,
  - Administration.
- Explained that the system would be one deployable backend with a shared relational database.
- Main advantages discussed:
  - simple deployment,
  - strong transactions,
  - easier testing and debugging,
  - lower operational complexity.
- Main disadvantages discussed:
  - the whole application is deployed and scaled together,
  - one module can affect the whole application,
  - the shared database can create coupling,
  - larger teams may have release coordination problems.

## 2026-10-28 — When the modular monolith may become difficult

- Discussed when the modular monolith could become painful:
  - search traffic becomes much larger than other traffic,
  - several teams need independent releases,
  - deployments and regression tests become slow,
  - one capability needs different technology or scaling,
  - failures in one module affect the rest of the system,
  - the shared database becomes a bottleneck,
  - module boundaries become unclear.
- Concluded that scale alone does not automatically require microservices.

## 2026-10-28 — Module communication discussion

- Discussed how modules should communicate without becoming tightly coupled.
- Each module should own its business rules and data.
- Modules should communicate through small public interfaces and stable identifiers.
- Modules should not directly use another module's repositories, ORM entities, or internal tables.
- Example discussed:
  - Requests receives a new service request,
  - Requests asks Profiles/Catalogue for necessary worker information,
  - Profiles/Catalogue returns only the required data,
  - Requests applies its own rules and stores the request.
- Also discussed synchronous calls, optional internal events, and composed read models.

## 2026-10-28 — Microservices discussion

- Discussed domain-oriented microservices as the second architecture.
- Different capabilities would be independent services with their own data.
- Main advantages:
  - independent deployment,
  - independent scaling,
  - stronger isolation,
  - possibility of different technologies.
- Main disadvantages:
  - network failures,
  - distributed consistency,
  - more complex monitoring and debugging,
  - higher operational complexity.
- Concluded that microservices could be useful later if independent scaling or separate teams become necessary.

## 2026-10-28 — Serverless event-driven discussion

- Discussed serverless event-driven architecture as the third option.
- Clarified that:
  - serverless means cloud-managed functions run when needed,
  - event-driven means parts of the system react to events.
- Example request flow was discussed using events such as `ServiceRequestCreated`.
- Main advantages:
  - automatic scaling,
  - useful for asynchronous tasks,
  - managed infrastructure.
- Main disadvantages:
  - eventual consistency,
  - retries,
  - duplicate or out-of-order events,
  - idempotency requirements,
  - harder tracing and debugging,
  - provider dependence.
- Concluded that this architecture is more suitable for asynchronous work than for the main transactional core.

## 2026-10-28 — Maintainability discussion

- Discussed which parts of RentYourExpert are likely to change most:
  - request lifecycle,
  - worker search and profiles,
  - authorization and moderation,
  - communication,
  - administration.
- Modular monolith was considered easier for connected business-rule changes.
- Microservices were considered better when capabilities need independent teams or deployment.
- Serverless/event-driven design was considered useful for adding independent asynchronous reactions.

## 2026-10-28 — Low-level implementation difficulties

- Discussed practical implementation problems for each architecture.
- For the modular monolith:
  - keeping module boundaries clean,
  - avoiding direct access to another module's tables,
  - handling concurrent request updates.
- For microservices:
  - API failures,
  - data synchronization,
  - distributed transactions,
  - tracing requests across services.
- For serverless/event-driven:
  - retries,
  - duplicate events,
  - idempotency,
  - debugging asynchronous workflows.

## 2026-10-28 — Final comparison and conclusion

- Compared the three architectures in terms of complexity, transactions, scaling, deployment, and maintainability.
- The layered modular monolith was considered the best initial fit for RentYourExpert.
- Main reasons:
  - the features are closely connected,
  - strong transactional consistency is useful,
  - development and deployment are simpler,
  - the current requirements do not justify distributed-system complexity.
- Microservices may become useful later if independent scaling or team ownership is needed.
- Serverless/event-driven mechanisms may be added later for asynchronous tasks such as notifications, audit, indexing, or analytics.