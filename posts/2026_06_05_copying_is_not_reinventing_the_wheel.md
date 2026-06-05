# Copying Is Not Reinventing the Wheel

Over the past few months I have been building, in my spare time, three pieces
of network infrastructure in Rust: a Layer 4 packet load balancer
([`lb`](https://github.com/thewillyhuman/lb)), a Layer 7 TLS-terminating
front end ([`gfe`](https://github.com/thewillyhuman/gfe)), and an
authoritative and recursive DNS server
([`dns`](https://github.com/thewillyhuman/dns)). Put together, they form the
spine of how traffic enters a datacenter: DNS resolves a name to a set of
virtual IPs, the L4 load balancer spreads packets across a fleet without
keeping per-connection state on any single box, and the L7 front end
terminates TLS once, centrally, and routes requests to the right backend.

None of this is novel. That is precisely the point of this post.

## The Shape of the Thing Already Existed

When people hear "I wrote my own load balancer," the reflexive reaction is
*why would you reinvent the wheel?* But I did not reinvent anything. I copied,
deliberately and with great care, a design that some of the best distributed
systems engineers in the world had already published.

`lb` is modeled on Google's **Maglev**, described in their NSDI '16 paper. The
core ideas — consistent hashing so that adding or removing a backend disturbs
the fewest possible flows, encapsulating packets with GRE so backends can
reply directly to the client (Direct Server Return), announcing virtual IPs
over BGP so routers spread connections via ECMP — are not my inventions. They
are Maglev's. `gfe` is modeled on Google's **GFE**, the General Front End:
terminate TLS once for the whole fleet so individual teams never touch a
certificate, keep the node stateless so the L4 layer can throw any connection
at any front end, route by host and path. Again, not my idea. Google's.

The architecture of unifying load balancing at L4 and terminating traffic
centrally at L7 is a solved problem. Google solved it, wrote it down, and
handed it to the rest of us. Refusing to use that knowledge would not have
made me clever. It would have made me slow.

## Reinventing the Wheel Is Something Else

There is a real failure mode that the phrase "reinventing the wheel" is meant
to warn against, and it is worth naming precisely so we do not confuse it with
what I actually did.

Reinventing the wheel is solving an *already-solved* problem from scratch, in
ignorance of the existing solution, and arriving at something worse. It is
re-deriving consistent hashing badly because you never read the paper. It is
inventing your own wire format when a perfectly good one exists. It is the
waste of effort *and* the waste of accumulated knowledge.

Copying a proven design is the exact opposite. It is the most efficient form
of engineering leverage there is. When I sat down to write the connection
tracking table in `lb`, I was not guessing whether per-flow affinity mattered
or how TCP state should drive entry expiry — Maglev had already taught me that
it does and roughly how. My job was not to discover the design. My job was to
*understand* it deeply enough to implement it correctly on my own hardware,
in my own language, for my own constraints.

That distinction — between copying a design and copying an implementation — is
the whole game. I did not vendor Google's code; they never published it. I
read what they explained about *why* the system is shaped the way it is, and
then I wrote every line myself. The understanding is mine. The blueprint was
borrowed, and borrowing a good blueprint is not a sin.

## Where the Real Work Lives

What surprised me is how much genuine engineering remains *after* you have
decided to copy a design. The paper tells you the destination; it does not
drive you there. Maglev's paper does not tell you how to make AF_XDP fall back
gracefully from native to SKB mode so the thing runs on a commodity Linux box
with no SmartNIC. GFE's design does not hand you a hot-reloadable config model
that swaps lookup tables atomically while in-flight requests keep flowing. The
papers describe the *what* and the *why*; every line of the *how* was still
mine to write, test, and get wrong a few times before getting right.

This is the same lesson I keep relearning. When I
[built a Kubernetes controller with Claude](2026_03_22_building_a_kubernetes_controller_with_ai.html),
the model produced the volume but the judgment — knowing which generated answer
was actually correct — stayed with me. When we
[lived through our Kafka outages](2025_11_29_kafka_outage_lessons.html), the
painful lesson was that adopting someone else's system without deeply
understanding its failure modes is its own kind of trap. Copying a design
without understanding it is just cargo-culting; understanding it and then
building it yourself is engineering.

## The Lesson Is Not Just About Code

This habit pays off well beyond load balancers. We have all walked into IT
departments carrying a sprawl of tiny, overlapping, untargeted services — one
team's bespoke deployment tool, another's half-finished internal portal, a
dozen one-off scripts nobody dares delete. Now look at how the public clouds
do it. They have ruthlessly optimized their catalog so that the *smallest*
possible set of well-built services covers the *vast majority* of what users
actually need. That is not a lack of ambition. It is the discipline of copying
a problem that has already been solved at scale: stop minting a new service for
every request, and offer the few that matter, done well.

The same is true of things engineers love to underestimate. When you do not
know how to build a user interface — or, more dangerously, when you *think* you
do — do not start from a blank canvas. Go find a tested, proven design and copy
it. The patterns that survive in good products survived because real users
validated them, often over years and millions of interactions. Reaching for one
of those is not laziness; it is refusing to relearn, at your users' expense, a
lesson someone has already paid for.

## Copy What Works

So my advice, mostly to a younger version of myself, is this: do not let the
fear of "reinventing the wheel" talk you out of building things, and do not let
the thrill of building things talk you into ignoring those who came before.

Read the papers. Read the postmortems. Read the
[blogs of brilliant engineers](2025_11_03_why_a_blog.html) who already hit the
walls you are about to walk into. Find the places where your problem has
already been solved, and copy what works — copy it shamelessly, copy it with
respect, copy the *reasoning* and not just the surface. The wheel is one of
humanity's best ideas precisely because we never stopped reusing it. Every cart,
every car, every landing gear is a copy. Nobody calls that reinvention.

In the end we are paid — and remembered — for the quality of what we deliver,
not for the heroism of the process that got us there. Nobody using the system
cares whether you derived every idea from first principles or borrowed the best
ones from people who already got it right. They care that it works. Copying
what works is not cutting a corner; it is keeping your eyes on the only thing
that actually matters.

The engineers who built Maglev and GFE did not want me to struggle in the dark.
They published so that the next person would not have to. Standing on their
shoulders is not a failure of originality. It is the entire reason they bothered
to write it down.
