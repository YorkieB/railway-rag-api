# AI Hallucination Research and Cursor Software

*Extracted from PDF*

---

## Page 1

Configuring
 
Cursor
 
AI
 
for
 
High-Fidelity
 
Code
 
Generation:
 
A
 
Technical
 
Framework
 
for
 
Hallucination
 
Mitigation
 
and
 
Context
 
Orchestration
 
Executive
 
Summary
 
The
 
paradigm
 
of
 
software
 
development
 
is
 
undergoing
 
a
 
fundamental
 
transformation,
 
shifting
 
from
 
an
 
era
 
defined
 
by
 
manual
 
syntax
 
generation
 
to
 
one
 
characterized
 
by
 
Context
 
Orchestration
.
 
In
 
this
 
new
 
reality,
 
the
 
Integrated
 
Development
 
Environment
 
(IDE)
 
ceases
 
to
 
be
 
a
 
passive
 
text
 
editor
 
and
 
evolves
 
into
 
an
 
active,
 
agentic
 
partner
 
capable
 
of
 
reasoning,
 
planning,
 
and
 
executing
 
complex
 
engineering
 
tasks.
 
Cursor
 
AI
 
represents
 
the
 
vanguard
 
of
 
this
 
shift,
 
embedding
 
Large
 
Language
 
Models
 
(LLMs)
 
directly
 
into
 
the
 
coding
 
workflow.
 
However,
 
the
 
efficacy
 
of
 
this
 
tool
 
is
 
not
 
inherent
 
in
 
the
 
software
 
itself;
 
rather,
 
it
 
is
 
contingent
 
upon
 
the
 
configuration,
 
constraints,
 
and
 
guidance
 
provided
 
by
 
the
 
human
 
operator.
 
The
 
probabilistic
 
nature
 
of
 
Generative
 
AI
 
introduces
 
a
 
critical
 
vulnerability:
 
hallucination
—the
 
confident
 
generation
 
of
 
factually
 
incorrect,
 
non-existent,
 
or
 
logically
 
flawed
 
code.
 
This
 
report
 
serves
 
as
 
an
 
exhaustive,
 
expert-level
 
manual
 
designed
 
to
 
bridge
 
the
 
gap
 
between
 
novice
 
utility
 
and
 
expert
 
mastery
 
of
 
the
 
Cursor
 
ecosystem.
 
Drawing
 
upon
 
deep
 
research
 
into
 
the
 
latest
 
software
 
release
 
(Cursor
 
v2.2,
 
December
 
2025),
 
this
 
analysis
 
details
 
the
 
precise
 
mechanisms
 
within
 
Cursor’s
 
settings
 
and
 
file
 
structures
 
that
 
allow
 
engineers
 
to
 
"program
 
the
 
programmer."
 
We
 
explore
 
the
 
transition
 
from
 
legacy
 
configuration
 
files
 
to
 
the
 
modern
 
.mdc
 
rule
 
system,
 
the
 
enforcement
 
of
 
Chain
 
of
 
Thought
 
(CoT)
 
processing
 
through
 
"Plan
 
Mode"
 
and
 
reasoning
 
models,
 
and
 
the
 
deployment
 
of
 
advanced
 
verification
 
agents
 
such
 
as
 
Debug
 
Mode
 
and
 
Multi-Agent
 
Judging
.
 
The
 
central
 
thesis
 
of
 
this
 
report
 
is
 
that
 
accuracy
 
is
 
a
 
function
 
of
 
constraint.
 
By
 
building
 
a
 
"fenced"
 
environment—where
 
the
 
AI
 
has
 
access
 
to
 
exactly
 
what
 
it
 
needs
 
and
 
absolutely
 
nothing
 
else—engineers
 
can
 
transform
 
Cursor
 
from
 
a
 
stochastic
 
parrot
 
into
 
a
 
deterministic,
 
expert-level
 
engineering
 
partner.
 
Chapter
 
1:
 
The
 
Stochastic
 
Nature
 
of
 
Generative
 
Code
 
and
 
the
 
Hallucination
 
Problem
 
To
 
effectively
 
combat
 
AI
 
hallucinations,
 
one
 
must
 
first
 
dispense
 
with
 
the
 
anthropomorphic
 
notion
 
that
 
the
 
AI
 
"knows"
 
code
 
in
 
the
 
human
 
sense.
 
When
 
a
 
human
 
developer
 
writes
 
a
 
function,
 
they
 
are
 
recalling
 
a
 
deterministic
 
rule
 
or
 
a
 
verified
 
memory.
 
When
 
an
 
AI
 
generates
 
a
 
function,
 
it
 
is
 
performing
 
a
 
statistical
 
calculation.
 
Understanding
 
this
 
distinction—the
 
difference
 
between
 
deterministic
 
recall
 
and
 
probabilistic
 
prediction
—is
 
the
 
foundational
 

## Page 2

step
 
toward
 
effective
 
mitigation.
 
1.1
 
The
 
Probabilistic
 
Engine:
 
The
 
Next-Token
 
Prediction
 
Game
 
At
 
its
 
most
 
fundamental
 
level,
 
the
 
Large
 
Language
 
Model
 
driving
 
Cursor
 
is
 
a
 
massive
 
statistical
 
calculator
 
designed
 
to
 
play
 
a
 
game
 
of
 
"guess
 
the
 
next
 
word."
 
It
 
has
 
been
 
trained
 
on
 
petabytes
 
of
 
text—books,
 
websites,
 
articles,
 
and
 
repositories—ingesting
 
the
 
statistical
 
correlations
 
between
 
billions
 
of
 
words,
 
or
 
"tokens".
1
 
When
 
a
 
user
 
inputs
 
a
 
prompt,
 
the
 
AI
 
does
 
not
 
query
 
a
 
database
 
of
 
facts.
 
Instead,
 
it
 
analyzes
 
the
 
sequence
 
of
 
tokens
 
in
 
the
 
prompt
 
and
 
calculates,
 
based
 
on
 
its
 
training
 
weights,
 
which
 
token
 
is
 
most
 
likely
 
to
 
follow.
 
This
 
process
 
is
 
governed
 
by
 
a
 
mathematical
 
function
 
known
 
as
 
Softmax
,
 
which
 
converts
 
raw
 
prediction
 
scores
 
(logits)
 
into
 
a
 
probability
 
distribution.
 
The
 
relationship
 
can
 
be
 
expressed
 
as:
 
 
$$P(x_i)
 
=
 
\frac{\exp(z_i
 
/
 
\tau)}{\sum_j
 
\exp(z_j
 
/
 
\tau)}$$
 
Where:
 
●
 
$P(x_i)$
 
is
 
the
 
probability
 
of
 
the
 
$i$-th
 
token
 
being
 
selected.
 
●
 
$z_i$
 
is
 
the
 
logit
 
(raw
 
score)
 
for
 
token
 
$i$.
 
●
 
$\tau$
 
is
 
the
 
Temperature
 
parameter.
 
When
 
the
 
model
 
encounters
 
a
 
prompt
 
for
 
which
 
it
 
lacks
 
sufficient
 
grounded
 
data—for
 
example,
 
a
 
request
 
for
 
a
 
niche
 
library
 
method
 
that
 
does
 
not
 
exist—it
 
utilizes
 
its
 
statistical
 
training
 
to
 
generate
 
the
 
most
 
"plausible"
 
next
 
sequence
 
of
 
characters.
2
 
If
 
the
 
training
 
data
 
contains
 
patterns
 
where
 
import
 
{
 
debounce
 
}
 
is
 
frequently
 
followed
 
by
 
from
 
"lodash",
 
but
 
the
 
user
 
requests
 
it
 
from
 
react,
 
the
 
model
 
may
 
hallucinate
 
import
 
{
 
debounce
 
}
 
from
 
"react"
 
simply
 
because
 
the
 
tokens
 
fit
 
the
 
syntactic
 
pattern,
 
even
 
if
 
the
 
library
 
export
 
does
 
not
 
exist.
3
 
This
 
phenomenon
 
is
 
not
 
a
 
failure
 
of
 
logic
 
in
 
the
 
traditional
 
sense
 
but
 
a
 
success
 
of
 
linguistic
 
coherence
 
over
 
factual
 
veracity.
 
The
 
model
 
is
 
optimizing
 
for
 
the
 
most
 
probable
 
continuation
 
of
 
the
 
text,
 
not
 
for
 
the
 
execution
 
of
 
the
 
code.
 
1.2
 
The
 
Taxonomy
 
and
 
Etiology
 
of
 
Code
 
Hallucinations
 
Hallucinations
 
in
 
the
 
context
 
of
 
generative
 
AI
 
for
 
software
 
engineering
 
are
 
not
 
monolithic;
 
they
 
manifest
 
in
 
distinct
 
categories,
 
each
 
requiring
 
different
 
mitigation
 
strategies.
 
Understanding
 
the
 
taxonomy
 
of
 
these
 
errors
 
is
 
crucial
 
for
 
configuring
 
the
 
appropriate
 
defenses.
1
 
1.2.1
 
Factual
 
Fabrication
 
(The
 
"Liar"
 
Hallucination)
 
This
 
involves
 
the
 
invention
 
of
 
entirely
 
new
 
entities
 
that
 
do
 
not
 
exist.
 
In
 
coding,
 
this
 
often
 
appears
 
as
 
Library
 
Fabrication
—the
 
AI
 
confidently
 
suggests
 
importing
 
a
 
method
 
that
 
sounds
 
plausible
 
but
 
is
 
not
 
part
 
of
 
the
 
library's
 
API
 
(e.g.,
 
pandas.read_pdf
 
or
 
react.useDebounce
 
where
 
it
 
doesn't
 
exist
 
natively).
 

## Page 3

●
 
Root
 
Cause:
 
Probabilistic
 
guessing
 
in
 
the
 
absence
 
of
 
specific
 
knowledge.
 
The
 
model
 
fills
 
the
 
gap
 
with
 
a
 
statistically
 
likely
 
token
 
sequence.
 
●
 
Mitigation:
 
This
 
requires
 
Grounding
 
tools
 
like
 
"Instant
 
Grep"
 
and
 
"Docs
 
Indexing"
 
to
 
force
 
the
 
model
 
to
 
verify
 
existence
 
before
 
generation.
4
 
1.2.2
 
Syntax
 
Mixing
 
(The
 
"Polyglot"
 
Hallucination)
 
This
 
occurs
 
when
 
the
 
model
 
conflates
 
syntax
 
from
 
different
 
languages
 
or
 
frameworks.
 
For
 
example,
 
using
 
Python's
 
snake_case
 
variable
 
naming
 
conventions
 
inside
 
a
 
JavaScript
 
project
 
that
 
strictly
 
enforces
 
camelCase,
 
or
 
attempting
 
to
 
use
 
React
 
Hooks
 
inside
 
a
 
Vue.js
 
component.
 
●
 
Root
 
Cause:
 
Pattern
 
bleeding
 
from
 
disparate
 
training
 
data
 
clusters.
 
The
 
model's
 
"attention
 
mechanism"
 
fails
 
to
 
prioritize
 
the
 
specific
 
language
 
constraint
 
over
 
the
 
general
 
coding
 
patterns
 
it
 
has
 
learned.
 
●
 
Mitigation:
 
This
 
requires
 
strict
 
Project
 
Rules
 
(via
 
.mdc
 
files)
 
that
 
explicitly
 
define
 
the
 
allowed
 
syntax
 
and
 
frameworks.
5
 
1.2.3
 
Logic
 
Drift
 
and
 
"Word
 
Salad"
 
Logic
 
drift
 
is
 
a
 
subtle
 
but
 
dangerous
 
form
 
of
 
hallucination
 
where
 
the
 
code
 
is
 
syntactically
 
correct
 
but
 
functionally
 
irrelevant
 
or
 
logically
 
flawed.
 
It
 
often
 
occurs
 
in
 
long-context
 
interactions
 
where
 
the
 
model
 
"forgets"
 
the
 
original
 
constraint
 
and
 
begins
 
to
 
ramble.
 
"Word
 
Salad"
 
is
 
a
 
more
 
severe
 
form
 
where
 
the
 
output
 
loses
 
structural
 
coherence
 
entirely.
 
●
 
Root
 
Cause:
 
Loss
 
of
 
context
 
over
 
long
 
token
 
sequences
 
and
 
the
 
inherent
 
limitations
 
of
 
next-token
 
prediction
 
without
 
reasoning.
 
●
 
Mitigation:
 
This
 
necessitates
 
Chain
 
of
 
Thought
 
(CoT)
 
protocols
 
and
 
Plan
 
Mode
,
 
which
 
force
 
the
 
model
 
to
 
reason
 
structurally
 
before
 
generating
 
code.
1
 
1.3
 
The
 
"Good
 
Test
 
Taker"
 
Syndrome
 
Why
 
does
 
the
 
AI
 
not
 
simply
 
say
 
"I
 
don't
 
know"?
 
The
 
answer
 
lies
 
in
 
the
 
Reinforcement
 
Learning
 
from
 
Human
 
Feedback
 
(RLHF)
 
process
 
used
 
to
 
train
 
these
 
models.
 
During
 
training,
 
models
 
are
 
rewarded
 
for
 
being
 
helpful,
 
fluent,
 
and
 
comprehensive.
 
They
 
are
 
essentially
 
trained
 
to
 
be
 
"good
 
test
 
takers"
 
who
 
get
 
more
 
credit
 
for
 
a
 
plausible
 
guess
 
than
 
for
 
leaving
 
an
 
answer
 
blank.
1
 
Research
 
indicates
 
that
 
hallucinations
 
persist
 
because
 
the
 
evaluation
 
metrics
 
used
 
to
 
grade
 
AI
 
performance
 
often
 
penalize
 
uncertainty.
 
If
 
a
 
model
 
refuses
 
to
 
answer
 
a
 
question,
 
it
 
is
 
deemed
 
"unhelpful."
 
Consequently,
 
the
 
model
 
learns
 
a
 
behavioral
 
pattern:
 
Always
 
provide
 
an
 
answer,
 
even
 
if
 
the
 
confidence
 
level
 
is
 
low.
 
It
 
adopts
 
an
 
authoritative
 
tone
 
regardless
 
of
 
its
 
factual
 
grounding,
 
effectively
 
"gaslighting"
 
the
 
developer.
 
To
 
mitigate
 
this,
 
the
 
configuration
 
must
 
explicitly
 
override
 
this
 
training.
 
We
 
must
 
provide
 
"System
 
Instructions"
 
that
 
give
 
the
 
model
 
"permission
 
to
 
fail"
—explicitly
 
authorizing
 
it
 
to
 
say
 

## Page 4

"I
 
don't
 
know"
 
rather
 
than
 
fabricating
 
a
 
solution.
2
 
Chapter
 
2:
 
The
 
Cursor
 
v2.2
 
Architecture
 
–
 
A
 
Paradigm
 
Shift
 
in
 
Context
 
Management
 
The
 
release
 
of
 
Cursor
 
v2.2
 
in
 
December
 
2025
 
marked
 
a
 
significant
 
evolution
 
in
 
the
 
tool's
 
architecture,
 
moving
 
beyond
 
simple
 
text
 
generation
 
to
 
a
 
sophisticated
 
system
 
of
 
Context
 
Management
 
and
 
Agentic
 
Verification
.
 
This
 
chapter
 
analyzes
 
the
 
specific
 
features
 
of
 
v2.2
 
that
 
are
 
critical
 
for
 
hallucination
 
mitigation.
 
2.1
 
The
 
Concept
 
of
 
the
 
"Storage
 
Area"
 
To
 
control
 
the
 
AI,
 
we
 
must
 
curate
 
its
 
environment.
 
A
 
primary
 
requirement
 
of
 
this
 
research
 
is
 
to
 
define
 
the
 
"storage
 
area"
 
for
 
guidance
 
files.
 
In
 
the
 
Cursor
 
ecosystem,
 
this
 
is
 
not
 
a
 
cloud
 
bucket
 
but
 
a
 
structured,
 
local
 
directory
 
that
 
lives
 
directly
 
inside
 
the
 
project
 
root.
5
 
The
 
directory
 
is
 
named
 
.cursor
.
 
Think
 
of
 
this
 
folder
 
as
 
the
 
AI’s
 
dedicated
 
"briefcase"
 
for
 
the
 
project.
 
Anything
 
placed
 
inside
 
this
 
directory
 
becomes
 
part
 
of
 
the
 
AI’s
 
permanent
 
instruction
 
set.
 
Because
 
it
 
resides
 
in
 
the
 
project
 
root,
 
it
 
is
 
version-controlled
 
(via
 
Git),
 
ensuring
 
that
 
the
 
AI
 
rules
 
travel
 
with
 
the
 
code
 
and
 
apply
 
consistently
 
to
 
every
 
developer
 
on
 
the
 
team.
5
 
The
 
architecture
 
of
 
this
 
storage
 
area
 
is
 
specific
 
and
 
hierarchical:
 
●
 
The
 
Root:
 
YourProject/.cursor/
 
●
 
The
 
Rules
 
Engine:
 
YourProject/.cursor/rules/
 
–
 
This
 
is
 
the
 
repository
 
for
 
behavioral
 
instructions,
 
specifically
 
the
 
modern
 
.mdc
 
files.
5
 
●
 
The
 
Planning
 
Archive:
 
YourProject/.cursor/plans/
 
–
 
This
 
directory
 
stores
 
the
 
artifacts
 
generated
 
by
 
"Plan
 
Mode,"
 
creating
 
a
 
persistent
 
memory
 
of
 
architectural
 
decisions
 
and
 
Chain
 
of
 
Thought
 
processes.
5
 
2.2
 
Multi-Agent
 
Judging
 
and
 
Parallel
 
Execution
 
One
 
of
 
the
 
most
 
powerful
 
anti-hallucination
 
features
 
introduced
 
in
 
v2.2
 
is
 
Multi-Agent
 
Judging
.
 
This
 
feature
 
leverages
 
the
 
statistical
 
improbability
 
of
 
multiple
 
independent
 
agents
 
hallucinating
 
the
 
exact
 
same
 
error
 
simultaneously.
9
 
Mechanism
 
of
 
Action:
 
When
 
a
 
user
 
initiates
 
a
 
complex
 
task
 
(often
 
requiring
 
the
 
"Composer"
 
or
 
specific
 
agentic
 
modes),
 
Cursor
 
can
 
spin
 
up
 
multiple
 
agents
 
in
 
parallel.
 
These
 
agents
 
may
 
operate
 
in
 
isolated
 
environments
 
(using
 
Git
 
worktrees)
 
to
 
prevent
 
file
 
conflicts.11
 
1.
 
Parallel
 
Generation:
 
Up
 
to
 
eight
 
agents
 
attempt
 
to
 
solve
 
the
 
same
 
prompt
 
independently.
 
2.
 
Consensus
 
and
 
Evaluation:
 
Once
 
the
 
agents
 
complete
 
their
 
tasks,
 
a
 
"Judge"
 
agent
 
(often
 
a
 
high-reasoning
 
model
 
like
 
Claude
 
3.7
 
or
 
GPT-4o)
 
evaluates
 
the
 
outputs.
 

## Page 5

3.
 
Selection:
 
The
 
system
 
compares
 
the
 
solutions
 
against
 
the
 
requirements
 
and
 
selects
 
the
 
"best"
 
one.
 
The
 
selected
 
solution
 
is
 
presented
 
to
 
the
 
user
 
with
 
a
 
comment
 
explaining
 
the
 
reasoning
 
behind
 
the
 
choice.
9
 
Hallucination
 
Mitigation:
 
If
 
Agent
 
A
 
hallucinates
 
a
 
non-existent
 
library
 
method,
 
but
 
Agents
 
B
 
and
 
C
 
use
 
standard,
 
verified
 
code,
 
the
 
Judge
 
agent
 
identifies
 
Agent
 
A
 
as
 
an
 
outlier
 
and
 
discards
 
its
 
output.
 
This
 
creates
 
an
 
automated
 
peer-review
 
system
 
that
 
filters
 
out
 
probabilistic
 
errors
 
before
 
they
 
reach
 
the
 
user.13
 
2.3
 
Debug
 
Mode:
 
The
 
Empirical
 
Verifier
 
Standard
 
AI
 
coding
 
is
 
"speculative"—the
 
AI
 
guesses
 
what
 
the
 
code
 
should
 
do.
 
Debug
 
Mode
,
 
introduced
 
in
 
v2.2,
 
changes
 
this
 
paradigm
 
by
 
introducing
 
empirical
 
verification.
14
 
The
 
Debug
 
Loop:
 
1.
 
Hypothesis:
 
When
 
a
 
bug
 
is
 
reported,
 
the
 
agent
 
scans
 
the
 
code
 
and
 
generates
 
hypotheses
 
about
 
the
 
root
 
cause.
 
2.
 
Instrumentation:
 
Instead
 
of
 
guessing
 
a
 
fix,
 
the
 
agent
 
instruments
 
the
 
code
 
with
 
logging
 
statements
 
(console.log,
 
print)
 
to
 
capture
 
actual
 
runtime
 
values.
 
3.
 
Reproduction:
 
The
 
user
 
(or
 
the
 
agent,
 
in
 
some
 
autonomous
 
configurations)
 
reproduces
 
the
 
bug.
 
4.
 
Analysis:
 
The
 
agent
 
reads
 
the
 
actual
 
runtime
 
logs.
 
It
 
sees
 
the
 
variable
 
states,
 
the
 
execution
 
path,
 
and
 
the
 
error
 
messages.
 
5.
 
Fix:
 
Based
 
on
 
this
 
empirical
 
data,
 
the
 
agent
 
proposes
 
a
 
targeted
 
fix.
15
 
This
 
mode
 
eliminates
 
"Logic
 
Drift"
 
hallucinations
 
where
 
the
 
AI
 
confidently
 
explains
 
a
 
bug
 
that
 
doesn't
 
exist.
 
By
 
forcing
 
the
 
AI
 
to
 
rely
 
on
 
runtime
 
data
 
rather
 
than
 
its
 
internal
 
predictions,
 
the
 
system
 
grounds
 
the
 
solution
 
in
 
reality.
17
 
2.4
 
Instant
 
Grep:
 
Grounding
 
in
 
the
 
Codebase
 
A
 
common
 
source
 
of
 
hallucination
 
is
 
the
 
AI
 
"imagining"
 
code
 
that
 
exists
 
elsewhere
 
in
 
the
 
project—referencing
 
a
 
utils.js
 
file
 
that
 
doesn't
 
exist
 
or
 
a
 
function
 
signature
 
that
 
is
 
different.
 
Instant
 
Grep
,
 
introduced
 
in
 
late
 
2025,
 
addresses
 
this
 
by
 
providing
 
the
 
agent
 
with
 
a
 
tool
 
to
 
perform
 
millisecond-latency
 
regex
 
searches
 
across
 
the
 
entire
 
codebase.
4
 
Before
 
generating
 
code
 
that
 
references
 
an
 
external
 
function,
 
the
 
agent
 
can
 
"grep"
 
the
 
codebase
 
to
 
verify
 
the
 
function's
 
existence
 
and
 
signature.
 
This
 
converts
 
the
 
AI's
 
memory
 
from
 
a
 
probabilistic
 
estimate
 
to
 
a
 
verified
 
fact,
 
significantly
 
reducing
 
"Resource
 
Invention"
 
hallucinations.
 
Chapter
 
3:
 
The
 
Command
 
Center
 
–
 
Mastering
 
Global
 
Configuration
 

## Page 6

Before
 
creating
 
project-specific
 
rules,
 
we
 
must
 
configure
 
the
 
global
 
environment
 
to
 
prioritize
 
accuracy.
 
These
 
settings,
 
accessed
 
via
 
Cmd/Ctrl
 
+
 
Shift
 
+
 
J
,
 
define
 
the
 
"personality"
 
of
 
the
 
AI
 
assistant
 
across
 
all
 
projects.
5
 
3.1
 
The
 
"Models"
 
Tab:
 
Selecting
 
the
 
AI's
 
Brain
 
The
 
choice
 
of
 
model
 
is
 
the
 
single
 
most
 
critical
 
configuration
 
for
 
enabling
 
reasoning.
 
Not
 
all
 
AI
 
models
 
are
 
capable
 
of
 
the
 
complex
 
Chain
 
of
 
Thought
 
(CoT)
 
processing
 
required
 
to
 
avoid
 
hallucinations.
 
Some
 
are
 
"fast
 
and
 
shallow"
 
(reflexive),
 
while
 
others
 
are
 
"slow
 
and
 
deep"
 
(reflective).
5
 
Model
 
Landscape
 
and
 
Recommendations:
 
Model
 
Name
 
Type
 
Best
 
Use
 
Case
 
Reasoning
 
Capability
 
(CoT)
 
Hallucination
 
Risk
 
o1-preview
 
/
 
o1-mini
 
Reasoning
 
Complex
 
architecture,
 
impossible
 
bugs,
 
math.
 
Very
 
High
 
(Native
 
CoT)
 
Lowest
 
Claude
 
3.7
 
Sonnet
 
Hybrid
 
General
 
coding,
 
refactoring,
 
nuanced
 
instructions.
 
High
 
(Extended
 
Thinking)
 
Low
 
Claude
 
3.5
 
Sonnet
 
Balanced
 
Daily
 
driver,
 
speed-sensitiv
e
 
tasks.
 
Moderate
 
(Implicit)
 
Moderate
 
Cursor
 
Small
 
Fast
 
Autocomplete,
 
quick
 
syntax
 
fixes.
 
Low
 
High
 
Configuration
 
Directive:
 
Navigate
 
to
 
Settings
 
>
 
Models.
 
Ensure
 
that
 
o1-preview
 
(or
 
o1-mini)
 
and
 
Claude
 
3.7
 
Sonnet
 
are
 
enabled.
 
If
 
available,
 
toggle
 
"Extended
 
Thinking"
 
for
 
Claude
 
3.7.18
 
These
 
models
 
are
 
architecturally
 
designed
 
to
 
"think"
 
before
 
they
 
speak,
 
generating
 
a
 
hidden
 
chain
 
of
 
thought
 
that
 
verifies
 
logic
 
and
 
reduces
 
the
 
likelihood
 
of
 
fabrication.1
 
Using
 
a
 
"Small"
 
model
 
for
 

## Page 7

complex
 
architectural
 
tasks
 
is
 
a
 
guarantee
 
of
 
hallucination.
 
3.2
 
The
 
"General"
 
Tab:
 
Establishing
 
the
 
"Literal
 
Intern"
 
Persona
 
The
 
"Rules
 
for
 
AI"
 
text
 
box
 
in
 
the
 
General
 
tab
 
defines
 
the
 
global
 
System
 
Prompt.
5
 
This
 
is
 
the
 
appropriate
 
place
 
to
 
set
 
the
 
AI's
 
baseline
 
behavior.
 
To
 
mitigate
 
the
 
"Good
 
Test
 
Taker"
 
syndrome,
 
we
 
must
 
establish
 
a
 
persona
 
of
 
extreme
 
caution—the
 
"Literal
 
Intern"
.
2
 
Recommended
 
Global
 
Configuration
 
Text:
 
Enter
 
the
 
following
 
text
 
into
 
the
 
"Rules
 
for
 
AI"
 
box
 
to
 
enforce
 
a
 
"truthfulness
 
bias":
 
"You
 
are
 
an
 
expert
 
pair
 
programmer
 
focused
 
on
 
factual
 
accuracy
 
and
 
code
 
safety.
 
1.
 
Permission
 
to
 
Fail:
 
If
 
you
 
are
 
unsure
 
of
 
an
 
answer,
 
a
 
library's
 
existence,
 
or
 
a
 
function
 
signature,
 
state
 
'I
 
do
 
not
 
know'
 
immediately.
 
Do
 
not
 
guess.
 
2.
 
Verification:
 
Before
 
using
 
any
 
external
 
library,
 
verify
 
it
 
is
 
standard
 
or
 
explicitly
 
present
 
in
 
the
 
project.
 
3.
 
Chain
 
of
 
Thought:
 
For
 
all
 
complex
 
logic,
 
explain
 
your
 
reasoning
 
step-by-step
 
before
 
generating
 
code.
 
4.
 
Context
 
Awareness:
 
Only
 
modify
 
files
 
explicitly
 
requested
 
or
 
strictly
 
necessary.
 
Show
 
surrounding
 
context
 
for
 
all
 
edits.
 
5.
 
No
 
Fluff:
 
Be
 
concise.
 
Avoid
 
moral
 
lectures.
 
Focus
 
on
 
the
 
code."
 
1
 
This
 
prompt
 
sets
 
a
 
"negative
 
constraint"
 
that
 
weighs
 
heavily
 
in
 
the
 
model's
 
attention
 
mechanism,
 
penalizing
 
guessing
 
and
 
rewarding
 
verification.
1
 
3.3
 
The
 
"Features"
 
Tab:
 
External
 
Documentation
 
Indexing
 
While
 
.cursor/rules
 
is
 
for
 
instructions
,
 
the
 
Docs
 
feature
 
is
 
for
 
knowledge
.
 
The
 
user
 
query
 
asks
 
about
 
"uploading
 
guidance
 
files
 
to
 
constrain
 
the
 
AI."
 
The
 
Docs
 
feature
 
allows
 
you
 
to
 
feed
 
the
 
AI
 
entire
 
documentation
 
libraries
 
to
 
constrain
 
it
 
to
 
verified
 
external
 
sources.
5
 
Configuration
 
Workflow:
 
1.
 
Navigate
 
to
 
Settings
 
>
 
Features
 
>
 
Docs
.
 
2.
 
Add
 
New
 
Doc:
 
Paste
 
the
 
URL
 
of
 
the
 
official
 
documentation
 
for
 
a
 
library
 
you
 
are
 
using
 
(e.g.,
 
the
 
Stripe
 
API,
 
the
 
React
 
docs,
 
or
 
a
 
specific
 
internal
 
library
 
documentation).
 
3.
 
Indexing:
 
Cursor
 
will
 
crawl
 
and
 
index
 
the
 
site,
 
storing
 
it
 
in
 
a
 
vector
 
database.
 
4.
 
Usage:
 
In
 
chat,
 
use
 
the
 
@
 
symbol
 
followed
 
by
 
the
 
doc
 
name
 
(e.g.,
 
@Stripe)
 
to
 
force
 
the
 
AI
 
to
 
read
 
that
 
specific
 
documentation
 
before
 
answering.
 
Constraint
 
Strategy:
 
By
 
typing
 
"Using
 
strictly
 
the
 
information
 
in
 
@Stripe...",
 
you
 
force
 
the
 
model
 
to
 
perform
 
Retrieval
 
Augmented
 
Generation
 
(RAG)
 
against
 
the
 
indexed
 
vectors
 
rather
 
than
 
relying
 
on
 
its
 
potentially
 
outdated
 
or
 
hallucinated
 
training
 
data.
5
 
Chapter
 
4:
 
Project
 
Rules
 
–
 
The
 
Modern.mdc
 
and
 

## Page 8

AGENTS.md
 
System
 
A
 
core
 
requirement
 
of
 
this
 
research
 
is
 
to
 
detail
 
"how
 
to
 
enter
 
project
 
rules"
 
and
 
"upload
 
guidance
 
files."
 
Cursor
 
has
 
evolved
 
from
 
a
 
legacy
 
single-file
 
system
 
to
 
a
 
robust,
 
multi-file
 
architecture
 
designed
 
for
 
scalability
 
and
 
precision.
 
4.1
 
The
 
Legacy
 
Trap:
 
.cursorrules
 
In
 
earlier
 
versions
 
of
 
Cursor,
 
users
 
were
 
instructed
 
to
 
create
 
a
 
single
 
file
 
named
 
.cursorrules
 
in
 
the
 
project
 
root.
 
While
 
this
 
is
 
still
 
supported
 
for
 
backward
 
compatibility,
 
it
 
is
 
deprecated
 
and
 
strongly
 
discouraged
 
for
 
the
 
detailed
 
requirements
 
of
 
professional
 
engineering.
5
 
The
 
Problem:
 
As
 
rules
 
accumulate
 
(Chain
 
of
 
Thought
 
protocols,
 
Coding
 
Styles,
 
Database
 
Schemas),
 
this
 
single
 
file
 
becomes
 
thousands
 
of
 
lines
 
long.
 
This
 
floods
 
the
 
context
 
window
 
(the
 
AI's
 
short-term
 
memory)
 
with
 
irrelevant
 
instructions,
 
creating
 
"noise"
 
that
 
confuses
 
the
 
model
 
and
 
leads
 
to
 
hallucinations.
 
4.2
 
The
 
Modern
 
Standard:
 
.mdc
 
(Markdown
 
for
 
Cursor)
 
The
 
recommended
 
solution
 
is
 
the
 
.mdc
 
file
 
system.
 
These
 
are
 
Markdown
 
files
 
located
 
specifically
 
in
 
the
 
.cursor/rules/
 
directory.
5
 
Anatomy
 
of
 
an
 
.mdc
 
File:
 
Every
 
.mdc
 
file
 
consists
 
of
 
two
 
parts:
 
the
 
Frontmatter
 
(metadata)
 
and
 
the
 
Body
 
(instructions).
 
The
 
Frontmatter
 
acts
 
as
 
a
 
routing
 
system,
 
controlling
 
when
 
the
 
rule
 
is
 
applied.7
 
Key
 
Frontmatter
 
Settings:
 
●
 
description
:
 
This
 
is
 
the
 
most
 
critical
 
setting.
 
It
 
tells
 
the
 
AI's
 
routing
 
agent
 
what
 
is
 
in
 
the
 
file.
 
When
 
"Apply
 
Intelligently"
 
is
 
active,
 
the
 
agent
 
scans
 
these
 
descriptions
 
to
 
decide
 
which
 
rules
 
to
 
load.
 
A
 
precise
 
description
 
(e.g.,
 
"Strict
 
guidelines
 
for
 
writing
 
Pytest
 
unit
 
tests")
 
ensures
 
the
 
rule
 
is
 
only
 
loaded
 
when
 
relevant,
 
keeping
 
the
 
context
 
window
 
clean
 
and
 
focused.
5
 
●
 
globs
:
 
This
 
uses
 
"File
 
Pattern
 
matching"
 
to
 
restrict
 
the
 
rule
 
to
 
specific
 
files.
 
○
 
Example:
 
globs:
 
"tests/**/*.py"
 
ensures
 
the
 
rule
 
only
 
applies
 
when
 
editing
 
Python
 
files
 
in
 
the
 
tests
 
directory.
 
○
 
Hallucination
 
Prevention:
 
This
 
prevents
 
the
 
AI
 
from
 
applying
 
frontend
 
rules
 
(like
 
"Use
 
React
 
Hooks")
 
to
 
backend
 
files,
 
a
 
common
 
source
 
of
 
"Syntax
 
Mixing"
 
hallucinations.
5
 
●
 
alwaysApply
:
 
A
 
boolean
 
toggle
 
(true/false).
 
○
 
false
 
(Recommended):
 
The
 
rule
 
is
 
applied
 
only
 
when
 
relevant
 
(based
 
on
 
description/globs).
 
This
 
saves
 
context
 
tokens.
 
○
 
true
 
(Use
 
Sparingly):
 
The
 
rule
 
is
 
forced
 
into
 
the
 
context
 
for
 
every
 
interaction.
 
This
 
should
 
be
 
reserved
 
for
 
"Constitutional"
 
rules
 
(e.g.,
 
"Always
 
use
 
TypeScript,"
 
"Never
 
reveal
 
secrets")
 
that
 
must
 
never
 
be
 
violated.
5
 

## Page 9

Table:
 
Comparison
 
of
 
Rule
 
Configuration
 
Methods
 
5
 
Feature
 
Legacy
 
Method
 
(.cursorrules)
 
Modern
 
Method
 
(.mdc)
 
Recommendation
 
File
 
Location
 
Project
 
Root
 
.cursor/rules/
 
Modern
 
Organization
 
Single
 
Monolithic
 
File
 
Multiple
 
Scoped
 
Files
 
Modern
 
Context
 
Logic
 
Always
 
Loaded
 
(Heavy)
 
Loaded
 
on
 
Demand
 
(Light)
 
Modern
 
Constraint
 
Power
 
Low
 
(Ambiguous)
 
High
 
(Precise
 
Globs)
 
Modern
 
Ease
 
of
 
Maintenance
 
Poor
 
Excellent
 
Modern
 
4.3
 
AGENTS.md:
 
The
 
High-Level
 
Context
 
In
 
addition
 
to
 
.mdc
 
rules,
 
Cursor
 
supports
 
a
 
file
 
named
 
AGENTS.md
 
in
 
the
 
project
 
root.
7
 
This
 
file
 
serves
 
as
 
a
 
"README
 
for
 
Agents."
 
●
 
Purpose:
 
To
 
provide
 
high-level
 
context
 
that
 
applies
 
to
 
the
 
entire
 
project
 
but
 
doesn't
 
fit
 
into
 
a
 
specific
 
behavioral
 
rule.
 
Examples
 
include
 
the
 
project's
 
architecture
 
overview,
 
build
 
commands,
 
and
 
testing
 
protocols.
 
●
 
Format:
 
Standard
 
Markdown
 
without
 
complex
 
frontmatter.
 
●
 
Usage:
 
It
 
is
 
automatically
 
read
 
by
 
the
 
agent
 
to
 
understand
 
the
 
broader
 
scope
 
of
 
the
 
project.
22
 
●
 
Best
 
Practice:
 
Use
 
AGENTS.md
 
to
 
explain
 
what
 
the
 
project
 
is,
 
and
 
.mdc
 
files
 
to
 
explain
 
how
 
to
 
write
 
the
 
code.
25
 
Chapter
 
5:
 
Chain
 
of
 
Thought
 
(CoT)
 
–
 
Configuration
 
and
 
Usage
 
The
 
user
 
query
 
specifically
 
emphasizes
 
the
 
need
 
for
 
Chain
 
of
 
Thought
 
(CoT)
.
 
This
 
is
 
the
 
single
 
most
 
important
 
"software"
 
solution
 
to
 
the
 
"hardware"
 
problem
 
of
 
probabilistic
 
guessing.
 
CoT
 
forces
 
the
 
model
 
to
 
generate
 
intermediate
 
reasoning
 
tokens,
 
which
 
serve
 
as
 
a
 

## Page 10

"scratchpad"
 
for
 
verification
 
before
 
the
 
final
 
answer
 
is
 
produced.
1
 
5.1
 
The
 
Native
 
Feature:
 
Plan
 
Mode
 
Cursor
 
has
 
a
 
built-in
 
mode
 
dedicated
 
to
 
CoT
 
called
 
Plan
 
Mode
.
5
 
●
 
Activation:
 
Press
 
Shift
 
+
 
Tab
 
in
 
the
 
chat
 
input
 
or
 
select
 
"Plan"
 
from
 
the
 
mode
 
dropdown.
26
 
●
 
The
 
CoT
 
Workflow:
 
1.
 
Research:
 
The
 
agent
 
scans
 
the
 
codebase
 
and
 
documentation
 
to
 
gather
 
facts.
 
2.
 
Drafting:
 
It
 
writes
 
a
 
step-by-step
 
plan
 
in
 
natural
 
language.
 
3.
 
Visualization
 
(v2.2):
 
The
 
agent
 
can
 
now
 
generate
 
inline
 
Mermaid
 
diagrams
 
(flowcharts,
 
sequence
 
diagrams)
 
to
 
visualize
 
the
 
architecture
 
before
 
writing
 
any
 
code.
6
 
This
 
visual
 
step
 
forces
 
the
 
model
 
to
 
verify
 
the
 
logical
 
flow
 
of
 
data.
 
4.
 
Review:
 
The
 
user
 
reviews
 
the
 
plan.
 
This
 
is
 
the
 
"Human-in-the-Loop"
 
check.
 
5.
 
Execution:
 
Code
 
generation
 
begins
 
only
 
after
 
the
 
plan
 
is
 
approved.
 
●
 
Hallucination
 
Mitigation:
 
This
 
enforces
 
a
 
"Measure
 
Twice,
 
Cut
 
Once"
 
philosophy.
 
The
 
plan
 
acts
 
as
 
a
 
grounding
 
document.
 
If
 
the
 
AI
 
proposes
 
a
 
non-existent
 
library
 
in
 
the
 
plan,
 
the
 
user
 
can
 
catch
 
it
 
before
 
any
 
code
 
is
 
written.
 
The
 
plans
 
are
 
stored
 
in
 
.cursor/plans/
 
for
 
future
 
reference.
8
 
5.2
 
Manual
 
CoT
 
Enforcement
 
via
 
Rules
 
For
 
users
 
who
 
want
 
to
 
force
 
CoT
 
in
 
every
 
interaction
 
(not
 
just
 
Plan
 
Mode),
 
a
 
specific
 
.mdc
 
rule
 
can
 
be
 
created
 
to
 
reprogram
 
the
 
AI's
 
output
 
format.
1
 
Implementation
 
Strategy:
 
Create
 
a
 
file
 
at
 
.cursor/rules/reasoning-protocol.mdc:
 
description:
 
Enforces
 
Chain
 
of
 
Thought
 
reasoning
 
for
 
all
 
complex
 
coding
 
tasks.
 
globs:
 
"*"
 
alwaysApply:
 
true
 
Chain
 
of
 
Thought
 
Protocol
 
For
 
every
 
request
 
that
 
involves
 
logic,
 
debugging,
 
or
 
refactoring,
 
you
 
MUST
 
strictly
 
follow
 
this
 
process:
 
1.
 
Thinking
 
Phase:
 
Before
 
writing
 
any
 
code,
 
output
 
a
 
block
 
wrapped
 
in
 
<thinking>
 
tags.
 
2.
 
Analysis:
 
Inside
 
the
 
tags,
 
break
 
down
 
the
 
user's
 
request.
 
List
 
the
 
files
 
you
 
will
 
modify
 
and
 
the
 
specific
 
steps
 
you
 
will
 
take.
 
3.
 
Self-Correction:
 
Ask
 
yourself,
 
"Is
 
there
 
a
 
simpler
 
way?
 
Does
 
this
 
break
 
any
 
existing
 
rules?
 
Does
 
this
 
library
 
actually
 
exist?"
 

## Page 11

4.
 
Execution:
 
Only
 
after
 
closing
 
the
 
</thinking>
 
tag,
 
provide
 
the
 
final
 
code.
 
By
 
"uploading"
 
this
 
guidance
 
file
 
to
 
your
 
storage
 
area,
 
you
 
effectively
 
reprogram
 
the
 
AI
 
to
 
always
 
show
 
its
 
work.
 
This
 
makes
 
debugging
 
the
 
AI
 
easier
 
because
 
if
 
it
 
writes
 
bad
 
code,
 
you
 
can
 
read
 
its
 
"Thinking"
 
block
 
to
 
see
 
exactly
 
where
 
it
 
hallucinated
 
(e.g.,
 
"I
 
will
 
use
 
the
 
pandas.read_pdf
 
function..."
 
->
 
User
 
catches
 
the
 
error
 
immediately).
 
Chapter
 
6:
 
Practical
 
Implementation
 
–
 
Constraint
 
Engineering
 
To
 
"constrain
 
the
 
AI
 
to
 
using
 
only
 
the
 
information
 
it
 
has
 
been
 
given,"
 
as
 
requested,
 
a
 
multi-layered
 
approach
 
is
 
required.
 
This
 
is
 
often
 
termed
 
Constraint
 
Engineering
.
 
6.1
 
Method
 
A:
 
The
 
"Closed
 
Context"
 
Prompt
 
When
 
utilizing
 
indexed
 
documentation
 
(from
 
the
 
Docs
 
feature)
 
or
 
uploaded
 
files,
 
the
 
user
 
must
 
explicitly
 
exclude
 
external
 
training
 
data.
1
 
The
 
AI's
 
default
 
behavior
 
is
 
to
 
use
 
both
 
its
 
training
 
data
 
and
 
your
 
context.
 
You
 
must
 
force
 
it
 
to
 
ignore
 
the
 
training
 
data.
 
●
 
The
 
Prompt:
 
"Using
 
@MyLibrary...
 
and
 
using
 
ONLY
 
the
 
information
 
in
 
that
 
document,
 
write
 
a
 
function
 
to
 
X.
 
Do
 
not
 
use
 
outside
 
knowledge
 
or
 
standard
 
libraries
 
if
 
they
 
conflict
 
with
 
the
 
documentation."
 
●
 
The
 
Mechanism:
 
This
 
negative
 
constraint
 
("Do
 
not",
 
"ONLY")
 
weighs
 
heavily
 
in
 
the
 
model's
 
attention
 
mechanism.
 
It
 
creates
 
a
 
high
 
penalty
 
for
 
accessing
 
the
 
parts
 
of
 
its
 
neural
 
network
 
that
 
contain
 
general
 
(and
 
potentially
 
hallucinated)
 
knowledge.
1
 
6.2
 
Method
 
B:
 
The
 
Rule-Based
 
Gatekeeper
 
Using
 
.mdc
 
files
 
to
 
create
 
"Gatekeeper
 
Rules"
 
is
 
highly
 
effective
 
for
 
enforcing
 
stack-specific
 
constraints.
5
 
Scenario:
 
Your
 
project
 
uses
 
an
 
older
 
version
 
of
 
a
 
library
 
(e.g.,
 
React
 
16),
 
but
 
the
 
AI
 
(trained
 
on
 
React
 
18)
 
constantly
 
hallucinates
 
modern
 
hooks
 
like
 
useId
 
that
 
don't
 
exist
 
in
 
your
 
version.
 
Implementation:
 
Create
 
.cursor/rules/tech-stack.mdc:
 
description:
 
Technical
 
stack
 
constraints
 
and
 
version
 
locking.
 
globs:
 
"**/*.{js,jsx,ts,tsx}"
 
alwaysApply:
 
true
 
Stack
 
Constraints
 
●
 
React
 
Version:
 
16.8
 
●
 
FORBIDDEN:
 
Do
 
not
 
use
 
useId,
 
useTransition,
 
or
 
useDeferredValue
 
(React
 
18
 
features).
 

## Page 12

●
 
FORBIDDEN:
 
Do
 
not
 
use
 
Tailwind
 
CSS.
 
Use
 
ONLY
 
styled-components.
 
●
 
If
 
a
 
user
 
request
 
implies
 
using
 
a
 
forbidden
 
feature,
 
REFUSE
 
the
 
request
 
and
 
explain
 
the
 
version
 
constraint.
 
This
 
forces
 
the
 
AI
 
to
 
align
 
with
 
the
 
specific
 
reality
 
of
 
the
 
project,
 
ignoring
 
its
 
general
 
training
 
on
 
newer
 
versions.
 
6.3
 
Method
 
C:
 
Parameter
 
Tuning
 
(Implicit
 
vs.
 
Explicit)
 
The
 
user
 
query
 
asks
 
about
 
setting
 
parameters
 
like
 
Temperature
 
and
 
Top-P
.
 
In
 
standard
 
LLM
 
interfaces,
 
these
 
are
 
sliders.
 
In
 
Cursor,
 
they
 
are
 
often
 
abstracted,
 
but
 
understanding
 
them
 
is
 
vital
 
for
 
"Programming
 
the
 
Programmer".
2
 
●
 
Temperature
 
($\tau$):
 
Controls
 
randomness.
 
For
 
code,
 
this
 
should
 
ideally
 
be
 
0.0
 
to
 
0.2
.
 
●
 
Top-P:
 
Controls
 
the
 
vocabulary
 
pool.
 
Should
 
be
 
low
 
(
0.1
)
 
to
 
prevent
 
"wildcard"
 
token
 
selection.
 
Cursor
 
Implementation:
 
As
 
of
 
late
 
2025,
 
Cursor
 
does
 
not
 
provide
 
direct
 
sliders
 
for
 
Temperature
 
in
 
the
 
main
 
chat
 
interface.28
 
However,
 
users
 
can
 
influence
 
these
 
parameters
 
via:
 
1.
 
Model
 
Selection:
 
"Reasoning"
 
models
 
like
 
o1-preview
 
are
 
tuned
 
for
 
lower
 
temperature/higher
 
determinism
 
by
 
default
 
compared
 
to
 
"Creative"
 
models.
 
2.
 
API
 
Configuration:
 
If
 
using
 
"Bring
 
Your
 
Own
 
Key"
 
(BYOK),
 
some
 
advanced
 
configurations
 
in
 
the
 
config.json
 
or
 
API
 
proxy
 
settings
 
may
 
allow
 
parameter
 
injection,
 
though
 
this
 
is
 
an
 
advanced
 
feature.
30
 
3.
 
Strict
 
Prompting:
 
Prompts
 
that
 
demand
 
"deterministic,"
 
"exact,"
 
or
 
"verbatim"
 
output
 
effectively
 
mimic
 
low-temperature
 
behavior
 
by
 
constraining
 
the
 
probabilistic
 
distribution
 
of
 
the
 
response.
1
 
Chapter
 
7:
 
Operational
 
Workflows
 
–
 
A
 
"For
 
Dummies"
 
Guide
 
To
 
synthesize
 
this
 
research
 
into
 
actionable
 
steps,
 
we
 
present
 
a
 
standardized
 
workflow
 
for
 
minimizing
 
hallucinations.
 
Step
 
1:
 
The
 
Setup
 
(One-Time)
 
1.
 
Open
 
Cursor
 
Settings
 
(
Cmd+Shift+J
).
 
2.
 
Models:
 
Enable
 
Claude
 
3.7
 
Sonnet
 
and
 
o1-preview.
 
3.
 
General:
 
Paste
 
the
 
"Literal
 
Intern"
 
system
 
prompt
 
(Chapter
 
3.2).
 
4.
 
Docs:
 
Index
 
the
 
official
 
URLs
 
for
 
your
 
project's
 
libraries.
 
Step
 
2:
 
The
 
Storage
 
Creation
 
1.
 
Create
 
a
 
folder
 
.cursor
 
in
 
your
 
project
 
root.
 
2.
 
Create
 
subfolders
 
rules
 
and
 
plans.
 

## Page 13

3.
 
Create
 
AGENTS.md
 
in
 
the
 
root
 
for
 
high-level
 
project
 
overview.
 
Step
 
3:
 
The
 
Constraint
 
Upload
 
1.
 
Create
 
.cursor/rules/stack.mdc.
 
2.
 
Define
 
your
 
specific
 
tech
 
stack
 
and
 
list
 
"FORBIDDEN"
 
libraries.
 
3.
 
Set
 
alwaysApply:
 
true
 
in
 
the
 
frontmatter.
 
Step
 
4:
 
The
 
Interaction
 
Loop
 
(Daily
 
Use)
 
1.
 
Simple
 
Tasks:
 
Use
 
standard
 
Chat.
 
The
 
.mdc
 
rules
 
will
 
guide
 
the
 
AI
 
silently.
 
2.
 
Complex
 
Logic:
 
Use
 
Plan
 
Mode
 
(Shift
 
+
 
Tab).
 
Review
 
the
 
plan/diagram
 
before
 
allowing
 
code
 
generation.
 
3.
 
Bugs:
 
Use
 
Debug
 
Mode
.
 
Let
 
the
 
agent
 
instrument
 
and
 
run
 
the
 
code
 
to
 
verify
 
the
 
fix
 
empirically.
 
4.
 
Critical
 
Features:
 
Use
 
Multi-Agent
 
Judging
 
(if
 
available
 
on
 
your
 
plan)
 
to
 
get
 
a
 
consensus-verified
 
solution.
 
Chapter
 
8:
 
Conclusion
 
Configuring
 
Cursor
 
AI
 
is
 
an
 
exercise
 
in
 
constraint
 
management
.
 
It
 
is
 
not
 
about
 
enabling
 
every
 
feature;
 
it
 
is
 
about
 
selectively
 
enabling
 
the
 
right
 
features
 
and
 
blocking
 
the
 
wrong
 
behaviors.
 
We
 
have
 
established
 
that
 
Cursor
 
possesses
 
a
 
dedicated
 
storage
 
area
 
(.cursor/rules
 
and
 
.cursor/plans)
 
that
 
enables
 
the
 
upload
 
of
 
guidance
 
files
 
in
 
the
 
form
 
of
 
.mdc
 
documents.
 
We
 
have
 
detailed
 
how
 
the
 
Frontmatter
 
in
 
these
 
files
 
(description,
 
globs,
 
alwaysApply)
 
acts
 
as
 
a
 
routing
 
system,
 
ensuring
 
the
 
AI
 
uses
 
the
 
right
 
information
 
at
 
the
 
right
 
time.
 
We
 
have
 
also
 
explored
 
the
 
critical
 
importance
 
of
 
Chain
 
of
 
Thought,
 
both
 
as
 
a
 
native
 
feature
 
(Plan
 
Mode,
 
Reasoning
 
Models)
 
and
 
as
 
a
 
manually
 
enforced
 
rule.
 
Finally,
 
we
 
have
 
highlighted
 
the
 
v2.2
 
innovations—Debug
 
Mode,
 
Multi-Agent
 
Judging,
 
and
 
Instant
 
Grep—as
 
powerful
 
tools
 
for
 
empirical
 
verification.
 
By
 
following
 
this
 
guide,
 
the
 
user
 
moves
 
beyond
 
the
 
phase
 
of
 
passive
 
usage
 
and
 
enters
 
the
 
expert
 
phase
 
of
 
active
 
orchestration.
 
You
 
are
 
no
 
longer
 
just
 
writing
 
code;
 
you
 
are
 
designing
 
the
 
cognitive
 
architecture
 
of
 
the
 
agent
 
that
 
writes
 
the
 
code
 
with
 
you.
 
The
 
"magic"
 
of
 
AI
 
is
 
not
 
in
 
the
 
model
 
itself,
 
but
 
in
 
the
 
context
 
you
 
build
 
around
 
it.
 
Appendix
 
A:
 
Reference
 
Tables
 
Table
 
1:
 
Configuration
 
File
 
Hierarchy
 
File/Location
 
Purpose
 
Scope
 
Recommendation
 

## Page 14

.cursor/rules/*.md
c
 
Specific
 
behavioral
 
rules
 
&
 
constraints.
 
Project
 
(Specific
 
Files)
 
Primary
 
method.
 
Use
 
for
 
90%
 
of
 
rules.
 
AGENTS.md
 
High-level
 
project
 
overview
 
&
 
architecture.
 
Project
 
(Global)
 
Use
 
for
 
"Readme"
 
style
 
context.
 
.cursorrules
 
Legacy
 
single-file
 
rules.
 
Project
 
(Global)
 
Avoid/Migrate.
 
Use
 
.mdc
 
instead.
 
.cursor/plans/
 
Storage
 
for
 
Plan
 
Mode
 
artifacts.
 
Project
 
(History)
 
Use
 
for
 
auditing
 
architectural
 
decisions.
 
Settings
 
>
 
General
 
System
 
prompt
 
&
 
Persona.
 
User
 
(Global)
 
Use
 
for
 
"Personality"
 
&
 
"Safety"
 
defaults.
 
Table
 
2:
 
Model
 
Capabilities
 
for
 
CoT
 
Model
 
Name
 
Type
 
Best
 
For
 
CoT
 
Capability
 
o1-preview
 
/
 
o1-mini
 
Reasoning
 
Algorithm
 
design,
 
complex
 
bugs.
 
Native.
 
"Thinks"
 
for
 
seconds/minutes.
 
Claude
 
3.7
 
Sonnet
 
Hybrid
 
General
 
coding,
 
high-fidelity
 
instructions.
 
Extended
 
Thinking.
 
Explicit
 
thought
 
blocks.
 
Claude
 
3.5
 
Sonnet
 
Balanced
 
Speed,
 
daily
 
refactoring.
 
Implicit.
 
Fast,
 
lower
 
reasoning
 
depth.
 
Cursor
 
Small
 
Fast
 
Autocomplete,
 
tab-completion.
 
None.
 
Pure
 
pattern
 
matching.
 

## Page 15

Table
 
3:
 
Hallucination
 
Troubleshooting
 
Guide
 
Symptom
 
Probable
 
Cause
 
Fix
 
Invented
 
Libraries
 
AI
 
assumes
 
generic
 
solution
 
exists.
 
Index
 
docs
 
in
 
Features
 
>
 
Docs
.
 
Use
 
"Instant
 
Grep".
 
Ignoring
 
Rules
 
Context
 
overload
 
or
 
vague
 
description.
 
Check
 
.mdc
 
description
.
 
Set
 
alwaysApply:
 
true
 
(carefully).
 
Logic
 
Errors
 
"Fast
 
thinking"
 
(guessing).
 
Switch
 
to
 
o1-preview
.
 
Use
 
Plan
 
Mode
.
 
Code
 
Rot/Drift
 
Speculative
 
fixing.
 
Use
 
Debug
 
Mode
 
to
 
run
 
code
 
and
 
generate
 
logs.
 
1
 
Works
 
cited
 
1.
 
Stopping
 
AI
 
Hallucinations:
 
A
 
Guide
 
2.
 
AI
 
Hallucination
 
Prevention
 
Settings
 
Guide
 
3.
 
Hallucinations
 
|
 
Cursor
 
Learn,
 
accessed
 
December
 
21,
 
2025,
 
https://cursor.com /learn/hallucination-lim itations
 
4.
 
Cursor
 
AI
 
IDE
 
tips,
 
tricks
 
&
 
best
 
practices
 
-
 
Keyboard
 
shortcuts,
 
Composer
 
mode,
 
.cursorrules
 
examples,
 
and
 
Reddit
 
communi ty
 
wisdom
 
-
 
GitHub,
 
accessed
 
December
 
21,
 
2025,
 
https://github.com /m urataslan1/cursor-ai-tips
 
5.
 
Cursor
 
AI
 
Configuration
 
Guide
 
6.
 
Changelog
 
·
 
Cursor,
 
accessed
 
December
 
21,
 
2025,
 
https://cursor.com /changelog
 
7.
 
rules___cursor_docs.pdf
 
8.
 
OpenAI
 
-
 
Mervin
 
Praison,
 
accessed
 
December
 
21,
 
2025,
 
https://m er.vin/category/ai/openai/
 
9.
 
Cursor
 
2.2:
 
Multi-Agent
 
Judging
 
-
 
Featured
 
Discussions ,
 
accessed
 
December
 
21,
 
2025,
 
https://forum .cursor.com /t/cursor-2-2-m ulti-agent-judging/1458 26
 
10.
 
accessed
 
December
 
21,
 
2025,
 
https://cursor.com /changelog/2-2#:~:text=W hen% 20run ning% 20m ultiple% 20age 
nts% 20in,all% 20parallel% 20agents% 20have% 20finished.
 
11.
 
Parallel
 
Agents
 
|
 
Cursor
 
Docs,
 
accessed
 
December
 
21,
 
2025,
 
https://cursor.com /docs/configuration/worktrees
 
12.
 
Debug
 
Mode,
 
Plan
 
Mode
 
Improvements,
 
Multi-Agent
 
Jud ging,
 
and
 
Pinned
 
Chats
 
-
 

## Page 16

Cursor,
 
accessed
 
December
 
21,
 
2025,
 
https://cursor.com /changelog/2-2
 
13.
 
Leveraging
 
LLMs
 
as
 
Meta-Judges:
 
A
 
Multi-Agent
 
Framework
 
for
 
Evaluating
 
LLM
 
Judgments,
 
accessed
 
December
 
21,
 
2025,
 
https://arxiv.org/htm l/2504.17087v1
 
14.
 
Cursor
 
2.2:
 
Debug
 
Mode
 
-
 
Featured
 
Discus sions,
 
accessed
 
December
 
21,
 
2025,
 
https://forum .cursor.com /t/cursor-2-2-debug-m ode/1458 28
 
15.
 
Introducing
 
Debug
 
Mode:
 
Agents
 
with
 
run time
 
logs
 
-
 
Cursor,
 
accessed
 
December
 
21,
 
2025,
 
https://cursor.com /blog/debug-m ode
 
16.
 
Modes
 
|
 
Cursor
 
Docs,
 
accessed
 
December
 
21,
 
2025,
 
https://cursor.com /docs/agent/m odes
 
17.
 
Designing
 
for
 
Novice
 
Debuggers:
 
A
 
Pilot
 
Stud y
 
on
 
an
 
AI-Assisted
 
Debugging
 
Tool
 
-
 
arXiv,
 
accessed
 
December
 
21,
 
2025,
 
https://arxiv.org/htm l/2509.21067v2
 
18.
 
Cursor
 
Now
 
Supports
 
Claude
 
3.7
 
Sonne t
 
-
 
Enh anc ed
 
AI
 
Programming
 
Experience,
 
accessed
 
December
 
21,
 
2025,
 
https://cursor101.com /article/cursor-claude-37
 
19.
 
Claude's
 
extended
 
thinking
 
-
 
Anthropic,
 
accessed
 
December
 
21,
 
2025,
 
https://w w w.anthropic.com /news/visible-extended-thinking
 
20.
 
Cursor
 
IDE
 
Rules
 
for
 
AI:
 
Guidelines
 
for
 
Specialized
 
AI
 
Assistant
 
-
 
Kirill
 
Markin,
 
accessed
 
December
 
21,
 
2025,
 
https://kirill-m arkin.com /articles/cursor-ide-rules-for-ai/
 
21.
 
Features
 
·
 
Cursor,
 
accessed
 
December
 
21,
 
2025,
 
https://cursor.com /features
 
22.
 
Rules
 
|
 
Cursor
 
Docs,
 
accessed
 
December
 
21,
 
2025,
 
https://cursor.com /docs/context/rules
 
23.
 
Mastering
 
.mdc
 
Files
 
in
 
Cursor:
 
Best
 
Practices
 
|
 
by
 
Venk at
 
-
 
Medium,
 
accessed
 
December
 
21,
 
2025,
 
https://m edium .com /@ ror.venkat/m astering-m dc-files-in-cur sor-best-practices-f 
535e670f651
 
24.
 
AGENTS.md,
 
accessed
 
December
 
21,
 
2025,
 
https://agents.m d/
 
25.
 
AGENTS.md:
 
A
 
New
 
Standard
 
for
 
Unified
 
Coding
 
Agent
 
Instruc tions
 
-
 
Addo
 
Zhang
 
-
 
Medium,
 
accessed
 
December
 
21,
 
2025,
 
https://addozhang.m edium .com /agents-m d-a-ne w-standard-for-unified-coding- 
agent-instructions-0635fc5cb759
 
26.
 
Cursor
 
tips
 
in
 
10
 
minutes,
 
accessed
 
December
 
21,
 
2025,
 
https://w w w.youtube.com /watch?v=Aib5N1IXLog&vl=en
 
27.
 
Cursor
 
2.2:
 
Plan
 
Mode
 
Improvements
 
-
 
Featured
 
Discus sions,
 
accessed
 
December
 
21,
 
2025,
 
https://forum .cursor.com /t/cursor-2-2-plan-m ode-im provem ents/1458 27
 
28.
 
Please
 
just
 
let
 
us
 
control
 
temperature
 
:
 
r/cur sor
 
-
 
Reddit,
 
accessed
 
December
 
21,
 
2025,
 
https://w w w.reddit.com /r/cursor/com m ents/1jm bvgb/please_just_let_us_control_t 
em perature/
 
29.
 
Possibility
 
to
 
set
 
temperature
 
-
 
Discussions
 
-
 
Cursor
 
-
 
Communi ty
 
Forum,
 
accessed
 
December
 
21,
 
2025,
 
https://forum .cursor.com /t/possibility-to-set-tem perature/147
 
30.
 
Configuration
 
|
 
Cursor
 
Docs,
 
accessed
 
December
 
21,
 
2025,
 
https://cursor.com /docs/cli/reference/configuration
 
