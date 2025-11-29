# Lessons Learned from Recent Kafka Outages

## The Unforeseen Vulnerability in Our Monitoring Stack

In the realm of monitoring, the team responsible for observing system health is
expected to be the last bastion of resilience. Paradoxically, recent events at
our workplace have highlighted a critical vulnerability within our own monitoring
infrastructure, leading to a series of outages that directly impacted our data
ingestion capabilities. Our primary buffer for all ingested data, Apache Kafka,
a component typically capacity-planned to retain data for up to three days,
failed us precisely when we needed it most. This redundancy is crucial, allowing
us to buffer data during backend unavailability and process backlogs by scaling
consumption when services recover.

## The Migration to OpenTelemetry and Its Unforeseen Challenges

Our ongoing migration from a Flume-based infrastructure to OpenTelemetry aims to
modernize our data pipeline. From a high-level perspective, our new architecture
involves frontends (proxies) forwarding user traffic to OpenTelemetry Collectors.
These collectors push data into various Kafka topics, which are subsequently
consumed and routed to their respective backends. For a considerable period,
this design functioned robustly. I recall instances of discovering primary
metrics backend unavailability for extended durations—sometimes two days—without
concern, confident in our ability to restore the backend and consume the buffered
backlog. While this approach introduces user-facing latency in metrics visibility
until data reaches the backend, it has been a deliberate management decision.

However, the last few weeks have brought a series of critical outages—not once,
but four times—culminating in one of our most significant operational nightmares.
At random intervals, Kafka inexplicably ceased accepting writes. This led our
new OpenTelemetry collectors to initiate disk buffering. Critically, after
approximately 15 minutes, the collectors exhausted their memory, as the disk
buffering mechanism is memory-mapped, leading to data rejection.

Another thing we just discovered is that when Kafka starts accepting writes
again (some blackouts were of 5 minutes) our collectors try to fetch all local
storage buffer at once and write it into Kafka as fast as possible, leading to
more OOMs.

## The Cascade of Failures

The frontends, detecting these rejections, began marking the affected collectors
as unhealthy, consequently shifting traffic to seemingly healthy collectors.
The ensuing traffic redistribution was so substantial that it triggered
Out-of-Memory (OOM) errors on the healthy collectors, which in turn were marked
unhealthy by the frontends. Concurrently, previously unhealthy collectors
attempted to recover and were briefly marked healthy, only to be overwhelmed
by the redirected traffic. This oscillatory pattern of collectors transitioning
between healthy and unhealthy states persisted, creating a "thundering herd"
effect, until manual intervention became unavoidable.

Our emergency procedure involved stopping all frontends, allowing all backend
collectors to stabilize and prepare for traffic, and then gradually re-enabling
traffic flow. Post-intervention, the system would return to a normal operational
state.

## Lessons Learned: The Price of Progress

The stark reality of these incidents is that we transitioned from an
established, albeit difficult-to-maintain, reliable infrastructure to a
newer, still-maturing, and currently unreliable one. This experience
underscores a fundamental principle in engineering: new systems, especially
those not entirely built in-house, necessitate a thorough understanding of their
operational characteristics and failure modes. The learning curve associated
with embracing new technologies often comes with unforeseen challenges, and it
is imperative to invest in deep operational knowledge to mitigate risks and
enhance system resilience. Our journey with OpenTelemetry and Kafka, while
promising for future scalability and flexibility, has provided a humbling
reminder that reliability is not merely an architectural decision but a
continuous process of learning, adaptation, and meticulous operational
refinement.
