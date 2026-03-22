# Building a Kubernetes Controller in a Sunday with Claude

For years, our teams at CERN had lived with one of those small operational
burdens that never quite justifies an incident report but quietly erodes
everyone's patience. Every time a Kubernetes Ingress was created or modified,
someone had to manually update DNS aliases in
[LanDB](https://landb.cern.ch) — CERN's central infrastructure database — using
the OpenStack CLI. Ad-hoc scripts existed, but they were fragile and
error-prone. Configuration drift between what Kubernetes declared and what
LanDB reflected was a constant risk, and every manual intervention was an
opportunity for human error. We had been asking for a proper solution for a long
time.

This Sunday, I sat down and built it. Together with Claude Opus, I wrote a
[Kubernetes controller](https://gitlab.cern.ch/gfacundo/landb-alias-controller)
that watches Ingress resources and automatically synchronizes their DNS aliases
with LanDB, and then packaged it into a
[Helm chart](https://gitlab.cern.ch/gfacundo/landb-alias-controller-helm-chart)
ready for deployment. Not a proof of concept — a deployable operator with proper
reconciliation logic, error handling, and release tags.

## When the Bottleneck Is No Longer Code

What struck me most about the experience was not the output itself, but what had
changed about the process. I knew exactly what I wanted to build. I understood
the LanDB API, the Kubernetes Ingress model, and the operational context that
shaped every design decision. What I lacked was the raw implementation time to
translate all of that into a working controller, its tests, and its packaging —
in a single sitting.

With the right model as a collaborator, the bottleneck was no longer writing
code. It was imagination and time. I drove the architecture, defined the
reconciliation behavior, and specified how the controller should interact with
LanDB. Claude handled the volume — scaffolding the operator, implementing the
reconciliation loop, wiring up the Helm chart. The collaboration felt less like
delegating and more like pair programming with someone who never gets tired and
types infinitely fast.

## Domain Knowledge Still Draws the Line

But this is not a story about AI replacing engineers. If anything, the
experience reinforced how essential domain knowledge remains. Claude can generate
a syntactically correct Kubernetes controller, but it cannot know that LanDB
treats alias ownership differently across network domains, or that certain
reconciliation edge cases only surface during CERN's infrastructure maintenance
windows. Only someone who has operated this infrastructure — who has been paged
at odd hours because of a DNS mismatch — can judge whether the generated code
is actually correct.

I learned this same lesson years ago while teaching at the University of Oviedo:
producing an answer is not the same as understanding why the answer is right.
The AI produces answers at remarkable speed. The engineer's job is to know which
ones are right.

## Trusting Through Testing

This raises a practical question: how do you trust code you didn't write line
by line? My answer was end-to-end tests. Rather than reviewing every generated
function in detail, I invested my time in writing comprehensive tests that
exercise the full reconciliation loop — creating Ingresses, verifying LanDB
updates, simulating failures, and confirming recovery. The tests became the
contract between my intent and the AI's output. If the tests pass, the
implementation honors the specification. If they don't, we iterate.

This is a pragmatic shift in how an engineer spends their time. Less reading
code, more designing verification. The tests don't just validate — they
document what the system is supposed to do, which matters even more when a
significant portion of the implementation was generated.

A few months ago I wrote that this blog's template engine was **my imagination
transformed into reality by software**. What changed since then is not the
imagination — it's how quickly it can become real. The controller is deployed,
the toil is gone, and one person accomplished in a Sunday what would have
previously taken weeks of accumulated effort. The engineer's role isn't
diminishing. It's shifting — toward judgment, design, and verification. And
honestly, those were always the parts that mattered most.
