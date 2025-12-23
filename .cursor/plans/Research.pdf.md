# Research.pdf

*Extracted from PDF*

---

## Page 1

 
 
JARVIS
 
MASTER
 
PLAN
 
A
 
complete
 
build
 
checklist,
 
feature
 
breakdown,
 
tooling
 
map,
 
documentation
 
system
 
(online/offline),
 
Cursor
 
workflow,
 
and
 
research
 
plan.
 
 
Contents
 
1.
 
Updated
 
master
 
to-do
 
list
 
(Phases
 
0–14)
 
 
2.
 
Live
 
sessions
 
(screen,
 
camera,
 
audio/video
 
calls,
 
avatar)
 
 
3.
 
Full
 
web
 
browser
 
control
 
(navigation
 
+
 
interaction)
 
 
4.
 
Full
 
computer
 
control
 
(Windows
 
companion)
 
 
5.
 
Agent
 
loop
 
(plan
 
→
 
act
 
→
 
verify
 
→
 
recover)
 
 
6.
 
Tools
 
&
 
services
 
architecture
 
map
 
 
7.
 
Documentation
 
system
 
(online/offline)
 
+
 
service
 
cards
 
+
 
Cursor
 
 
8.
 
Research
 
checklist
 
(with
 
outputs
 
and
 
decisions
 
unlocked)
 
 
 
1)
 
Updated
 
master
 
to-do
 
list
 
Phase
 
0
 
—
 
Specs,
 
scope,
 
and
 
rules
 

## Page 2

●
 
Write
 
mission
 
+
 
boundaries
 
(what
 
Jarvis
 
is
 
/
 
is
 
not)
 
 
●
 
Define
 
top
 
10
 
use-cases
 
+
 
required
 
output
 
formats
 
(checklists/PDF/code)
 
 
●
 
Define
 
MVP
 
vs
 
V1
 
vs
 
V2
 
scope
 
(one
 
page)
 
 
●
 
Define
 
persona
 
+
 
tone
 
rules
 
(how
 
Jarvis
 
speaks/acts)
 
 
●
 
Define
 
uncertainty
 
protocol
 
(use
 
[Uncertain],
 
ask
 
clarifying
 
questions)
 
 
●
 
Define
 
privacy
 
rules
 
(especially
 
live
 
+
 
automation)
 
 
●
 
Define
 
cost
 
targets
 
(daily
 
cap,
 
per-session
 
cap)
 
 
●
 
Draft:
 
 
○
 
PRD
 
(Product
 
Requirements
 
Doc)
 
 
○
 
Technical
 
spec
 
(architecture
 
+
 
data
 
flows)
 
 
○
 
Safety/Privacy
 
spec
 
(refusals,
 
retention,
 
logging,
 
permissions)
 
 
Phase
 
1
 
—
 
Core
 
platform
 
foundations
 
(accounts,
 
storage,
 
security)
 
Auth
 
●
 
Login
 
/
 
Register
 
/
 
Forgot
 
Password
 
UI
 
 
●
 
Backend
 
auth
 
endpoints
 
+
 
session
 
handling
 
 
●
 
Route
 
protection
 
 
Data
 
models
 
●
 
Users
 
 

## Page 3

●
 
Projects
 
 
●
 
Conversations
 
 
●
 
Messages
 
 
●
 
Files
 
(original
 
+
 
extracted
 
text
 
+
 
metadata)
 
 
●
 
Memories
 
(global
 
+
 
project)
 
 
●
 
LiveSessions
 
 
●
 
ToolCalls
 
/
 
AutomationRuns
 
(audit
 
trail)
 
 
●
 
BrowserSessions
 
 
●
 
DeviceAgents
 
(local
 
companion
 
pairing)
 
 
Security
 
●
 
Secrets
 
management
 
(no
 
keys
 
in
 
code)
 
 
●
 
Log
 
redaction
 
(mask
 
API
 
keys/tokens/password
 
patterns)
 
 
●
 
HTTPS
 
everywhere
 
 
●
 
Rate
 
limiting
 
+
 
basic
 
abuse
 
protection
 
 
Phase
 
2
 
—
 
Main
 
UI
 
(your
 
50/50
 
split)
 
●
 
Resizable
 
50/50
 
split
 
panes
 
(save
 
per
 
user)
 
 
●
 
Right
 
pane
 
tabs:
 
Files
 
|
 
Sources
 
|
 
Settings
 
|
 
Live
 
|
 
Control
 
 
●
 
Mobile
 
fallback
 
layout
 
(stacked
 
panels)
 
 
●
 
Global
 
STOP
 
/
 
Panic
 
Stop
 
design
 
reserved
 
 

## Page 4

Phase
 
3
 
—
 
Projects
 
(workspaces)
 
●
 
Create/rename/delete
 
projects
 
 
●
 
Project
 
switcher
 
always
 
visible
 
 
●
 
Hard
 
separation
 
per
 
project:
 
chats,
 
files,
 
(optional)
 
project
 
memory
 
 
Phase
 
4
 
—
 
Chat
 
+
 
conversation
 
history
 
●
 
Chat
 
composer
 
+
 
message
 
list
 
 
●
 
Streaming
 
responses
 
 
●
 
Stop
 
generating
 
 
●
 
Regenerate
 
response
 
 
●
 
Edit
 
last
 
user
 
message
 
→
 
re-run
 
 
●
 
Save/load
 
conversation
 
history
 
 
●
 
Conversation
 
list
 
per
 
project
 
 
●
 
(V1)
 
Search
 
conversations
 
 
●
 
(V1)
 
Pin
 
conversations
 
 
Phase
 
5
 
—
 
Knowledge
 
base
 
(RAG)
 
from
 
your
 
documents
 
Upload
 
+
 
extraction
 
●
 
Upload
 
UI
 
(drag/drop
 
+
 
attach
 
in
 
chat)
 
 
●
 
File
 
validation
 
(MVP:
 
PDF,
 
DOCX,
 
TXT)
 
 

## Page 5

●
 
Extract
 
text
 
+
 
store
 
extracted
 
content
 
 
●
 
Store
 
originals
 
+
 
metadata
 
 
Indexing
 
(async)
 
●
 
Chunking
 
strategy
 
 
●
 
Embeddings
 
generation
 
 
●
 
Store
 
vectors
 
+
 
metadata
 
 
●
 
Re-index
 
button
 
 
Retrieval
 
●
 
Retrieve
 
top-k
 
chunks
 
 
●
 
Inject
 
into
 
model
 
context
 
 
●
 
Sources
 
panel
 
with
 
snippet
 
previews
 
 
●
 
If
 
retrieval
 
is
 
empty
 
→
 
Jarvis
 
must
 
say
 
so
 
(no
 
guessing)
 
 
Phase
 
6
 
—
 
Memory
 
+
 
personalization
 
●
 
Memory
 
policy
 
(what’s
 
saved;
 
permission
 
rules)
 
 
●
 
Global
 
memory
 
+
 
project
 
memory
 
 
●
 
UI:
 
memory
 
toggle
 
on/off
 
 
●
 
UI:
 
view/edit/delete
 
memory
 
items
 
 
●
 
Private
 
sessions
 
mode
 
(no
 
memory
 
+
 
reduced
 
retention)
 
 

## Page 6

Phase
 
7
 
—
 
Exporting
 
+
 
structured
 
outputs
 
(PDF-first)
 
●
 
Export
 
single
 
answer
 
→
 
PDF
 
 
●
 
Export
 
whole
 
conversation
 
→
 
PDF
 
 
●
 
Export
 
selected
 
messages
 
→
 
PDF
 
 
●
 
PDF
 
template:
 
title,
 
project
 
name,
 
timestamp,
 
headings,
 
code
 
blocks,
 
sources
 
 
Phase
 
8
 
—
 
Safety
 
+
 
quality
 
controls
 
●
 
Refusal
 
policy
 
+
 
safe
 
redirects
 
 
●
 
Uncertainty
 
protocol
 
enforcement
 
 
●
 
Tool
 
failure
 
handling
 
+
 
graceful
 
fallback
 
modes
 
 
●
 
Build
 
Jarvis
 
eval
 
pack:
 
 
○
 
50–100
 
real
 
prompts
 
you’ll
 
use
 
 
○
 
expected
 
format
 
checks
 
 
○
 
regression
 
tests
 
after
 
changes
 
 
 
2)
 
Live
 
sessions
 
(ALL
 
options)
 
LS0
 
—
 
Foundations
 
(shared)
 
●
 
LiveSession
 
model
 
+
 
lifecycle
 
(Idle
 
→
 
Connecting
 
→
 
Live
 
→
 
Paused
 
→
 
Ended)
 
 

## Page 7

●
 
Live
 
tab
 
UI
 
(start/stop
 
+
 
toggles
 
mic/cam/screen)
 
 
●
 
Permissions
 
UX
 
(deny/allow/device
 
missing)
 
 
●
 
Transcript
 
stream
 
always
 
 
●
 
Privacy
 
default:
 
no
 
raw
 
audio/video
 
stored
 
 
●
 
Session
 
budgets
 
(minutes
 
+
 
tokens)
 
 
●
 
Always-visible
 
LIVE
 
indicator
 
(what’s
 
active)
 
 
●
 
One-click
 
Panic
 
Stop
 
(kills
 
mic/cam/screen
 
instantly)
 
 
LS3
 
—
 
Screen
 
share
 
assist
 
(highest
 
ROI)
 
●
 
Start
 
screen
 
share
 
(tab/window)
 
 
●
 
Preview
 
tile
 
 
●
 
Frame
 
sampling
 
(start
 
low:
 
~1
 
fps)
 
 
●
 
“Describe
 
what
 
you
 
see”
 
 
●
 
“Guide
 
me
 
step-by-step”
 
(numbered
 
steps
 
+
 
copy
 
buttons)
 
 
●
 
“Pin
 
frame”
 
snapshot
 
 
●
 
Secret
 
detection
 
warnings
 
(API
 
key
 
patterns)
 
 
●
 
Fallback:
 
upload
 
screenshot
 
 
LS2
 
—
 
Camera
 
vision
 
●
 
Enable
 
camera
 
+
 
preview
 
tile
 
 
●
 
Frame
 
sampling
 
+
 
analysis
 
 

## Page 8

●
 
Task
 
mode
 
(“Help
 
me
 
do
 
X”)
 
 
●
 
Region-of-interest
 
selection
 
(tap/click
 
focus
 
area)
 
 
●
 
Purge
 
on
 
end
 
(default)
 
 
LS1A
 
—
 
Audio
 
call
 
●
 
WebRTC
 
audio
 
start/end
 
 
●
 
Streaming
 
STT
 
partial
 
transcripts
 
 
●
 
Turn
 
detection
 
 
●
 
Streaming
 
LLM
 
output
 
 
●
 
Streaming
 
TTS
 
playback
 
 
●
 
Barge-in
 
(user
 
speaks
 
→
 
stop
 
TTS
 
immediately)
 
 
●
 
Call
 
UI:
 
mute,
 
push-to-talk,
 
captions
 
 
LS1B
 
—
 
Video
 
call
 
●
 
Add
 
local
 
video
 
feed
 
 
●
 
Network
 
adaptation
 
 
●
 
Camera
 
on/off,
 
device
 
select
 
 
●
 
Optional:
 
sample
 
frames
 
for
 
context
 
 
LS1C
 
—
 
Jarvis
 
presence/avatar
 
●
 
Orb/waveform
 
synced
 
to
 
voice
 
amplitude
 
 

## Page 9

●
 
States:
 
listening/thinking/speaking
 
 
●
 
Optional:
 
2D
 
avatar
 
lip
 
sync
 
 
●
 
Optional:
 
talking
 
head
 
pipeline
 
(do
 
last)
 
 
 
3)
 
Full
 
web
 
browser
 
control
 
(navigation
 
+
 
interaction)
 
Core
 
principle
 
Jarvis
 
must
 
operate
 
as
 
a
 
controlled
 
agent:
 
Plan
 
→
 
step
 
execution
 
→
 
verify
 
after
 
each
 
step
 
→
 
recover/pause
 
→
 
require
 
approvals
 
for
 
risky
 
actions
 
BC0
 
—
 
Foundations
 
●
 
Choose
 
automation
 
approach
 
(DOM-first)
 
 
●
 
BrowserSession
 
model
 
(tabs,
 
URL,
 
status)
 
 
●
 
Commands:
 
open
 
URL,
 
back/forward/refresh,
 
new
 
tab/close
 
tab/switch
 
tab
 
 
●
 
Scroll,
 
find
 
text
 
on
 
page
 
 
●
 
Observation
 
pipeline:
 
URL/title
 
+
 
DOM
 
snapshot
 
/
 
accessibility
 
tree
 
+
 
screenshots
 
 
BC1
 
—
 
Reliable
 
interactions
 
●
 
Click
 
by
 
selector
 
 

## Page 10

●
 
Click
 
by
 
visible
 
text/role
 
(“click
 
button
 
that
 
says
 
Sign
 
in”)
 
 
●
 
Type
 
into
 
inputs
 
(mask
 
passwords)
 
 
●
 
Dropdowns,
 
checkboxes,
 
radios
 
 
●
 
Handle
 
cookie
 
banners
 
+
 
modals/popups
 
 
BC2
 
—
 
Verification
 
+
 
recovery
 
●
 
Verify
 
each
 
step
 
(URL
 
change,
 
element
 
present,
 
confirmation)
 
 
●
 
Detect
 
stuck
 
states:
 
captcha,
 
login
 
wall,
 
error
 
pages
 
 
●
 
“User
 
takeover”
 
(pause
 
automation,
 
let
 
you
 
do
 
the
 
step,
 
then
 
resume)
 
 
BC3
 
—
 
Safety
 
guardrails
 
●
 
Domain
 
allowlist/denylist
 
 
●
 
Confirm
 
gates:
 
payments,
 
deletes,
 
sending
 
messages/posts,
 
downloads/installs
 
 
●
 
Never
 
auto-handle
 
2FA
 
(pause
 
and
 
prompt
 
you)
 
 
●
 
Action
 
rate
 
limits
 
 
BC4
 
—
 
UI
 
●
 
Control
 
panel:
 
current
 
URL
 
+
 
status
 
 
●
 
Plan
 
preview
 
before
 
running
 
 
●
 
Step-by-step
 
approvals
 
(approve/deny)
 
 
●
 
BIG
 
STOP
 
button
 
 

## Page 11

●
 
Action
 
log
 
+
 
downloadable
 
run
 
report
 
 
 
4)
 
Full
 
computer
 
control
 
(Windows
 
companion)
 
CC0
 
—
 
Local
 
companion
 
foundation
 
●
 
Build
 
local
 
Windows
 
companion
 
app/service
 
 
●
 
Secure
 
pairing
 
with
 
cloud
 
Jarvis
 
(device
 
key)
 
 
●
 
Permission
 
tiers:
 
Read-only
 
→
 
Limited
 
→
 
Full
 
(explicit
 
enable)
 
 
●
 
Keep
 
credentials
 
local
 
(never
 
upstream)
 
 
CC1
 
—
 
Minimum
 
OS
 
action
 
set
 
●
 
Launch/close
 
apps
 
 
●
 
Focus/switch
 
windows
 
 
●
 
Keyboard
 
shortcuts
 
+
 
controlled
 
typing
 
 
●
 
File
 
operations
 
rules:
 
 
○
 
read-only
 
folders
 
allowed
 
 
○
 
write/delete/move/rename
 
requires
 
confirmation
 
 
●
 
Clipboard
 
handling
 
with
 
redaction
 
 

## Page 12

CC2
 
—
 
Screen-based
 
fallback
 
automation
 
●
 
Screenshot
 
understanding
 
(vision)
 
 
●
 
Click
 
targeting
 
with
 
visual
 
anchors
 
 
●
 
“Show
 
click
 
target
 
before
 
clicking”
 
overlay
 
 
●
 
Region-of-control
 
(only
 
act
 
inside
 
a
 
chosen
 
window/box)
 
 
CC3
 
—
 
Guardrails
 
●
 
Blocklist
 
sensitive
 
apps
 
by
 
default
 
(password
 
managers,
 
banking,
 
system
 
security)
 
 
●
 
Confirmations
 
for
 
destructive
 
actions
 
 
●
 
Always-visible
 
“Automation
 
Active”
 
indicator
 
 
●
 
Panic
 
Stop
 
kills
 
automation
 
instantly
 
 
 
5)
 
Agent
 
loop
 
(plan
 
→
 
act
 
→
 
verify
 
→
 
recover)
 
●
 
Planner:
 
generates
 
step
 
plan
 
+
 
checkpoints
 
 
●
 
Executor:
 
runs
 
one
 
step
 
at
 
a
 
time
 
 
●
 
Verifier:
 
confirms
 
success
 
criteria
 
after
 
each
 
step
 
 
●
 
Recovery:
 
retry
 
alternate
 
approach
 
OR
 
ask
 
you
 
OR
 
pause/handoff
 
 
●
 
Explainability
 
toggle
 
(“why
 
this
 
step?”)
 
 

## Page 13

●
 
Draft
 
mode
 
(suggest
 
only;
 
no
 
execution)
 
 
 
6)
 
Tools
 
&
 
services
 
architecture
 
map
 
Recommended
 
stack
 
(Google
 
Cloud
 
friendly)
 
●
 
Backend
 
API:
 
Google
 
Cloud
 
Run
 
 
●
 
Files/PDFs:
 
Cloud
 
Storage
 
 
●
 
Secrets:
 
Secret
 
Manager
 
 
●
 
Queue:
 
Cloud
 
Tasks
 
 
●
 
Structured
 
DB:
 
Postgres
 
(Cloud
 
SQL)
 
or
 
Firestore
 
 
●
 
Vector
 
DB:
 
Qdrant
 
 
●
 
Logging:
 
Cloud
 
Logging
 
 
●
 
Browser
 
automation:
 
Playwright
 
 
●
 
Voice/live:
 
Realtime
 
stack
 
OR
 
streaming
 
STT
 
+
 
streaming
 
TTS
 
 
●
 
OS
 
control:
 
local
 
Windows
 
“Jarvis
 
Companion”
 
 
●
 
Dev
 
tooling:
 
Cursor
 
(+
 
repo
 
rules)
 
 
 
7)
 
Documentation
 
system
 
(online/offline)
 
+
 
service
 
cards
 
+
 
Cursor
 

## Page 14

Your
 
docs
 
system
 
(offline-first,
 
versioned)
 
●
 
Create
 
/docs
 
repo
 
(Markdown)
 
 
●
 
Publish
 
docs
 
site
 
(online)
 
+
 
offline
 
export
 
(ZIP/PDF)
 
 
●
 
Index
 
your
 
docs
 
into
 
Jarvis
 
RAG
 
so
 
Jarvis
 
can
 
answer
 
from
 
your
 
manuals
 
 
●
 
Add
 
versioning
 
+
 
changelog
 
 
Manuals
 
to
 
write
 
●
 
Jarvis
 
User
 
Manual
 
 
●
 
Jarvis
 
Operator
 
Manual
 
(ops/runbooks)
 
 
●
 
Security
 
&
 
Privacy
 
Guide
 
 
●
 
Knowledge
 
Base
 
(RAG)
 
Guide
 
 
●
 
Live
 
Sessions
 
Guide
 
 
●
 
Browser
 
Control
 
Guide
 
 
●
 
Windows
 
Companion
 
Guide
 
 
●
 
Troubleshooting
 
Playbook
 
 
●
 
Release
 
Notes
 
template
 
 
Service
 
Cards
 
(one
 
per
 
tool/service)
 
Each
 
card:
 
purpose,
 
setup,
 
permissions/IAM,
 
limits,
 
common
 
errors,
 
“how
 
we
 
run
 
this”.
 
●
 
Cloud
 
Run
 
 

## Page 15

●
 
Cloud
 
Storage
 
 
●
 
Secret
 
Manager
 
 
●
 
Cloud
 
Tasks
 
 
●
 
Cloud
 
SQL
 
/
 
Firestore
 
 
●
 
Qdrant
 
 
●
 
Cloud
 
Logging
 
 
●
 
Playwright
 
 
●
 
Realtime
 
/
 
STT
 
/
 
TTS
 
choice
 
 
●
 
Windows
 
Companion
 
(your
 
app)
 
 
●
 
Cursor
 
 
Cursor
 
(developer
 
workflow)
 
●
 
Cursor
 
Service
 
Card
 
 
●
 
Cursor
 
Workflow
 
Guide
 
(small
 
diffs,
 
review
 
checklist,
 
when
 
to
 
use
 
agent
 
modes)
 
 
●
 
Add
 
.cursor/rules/
 
in
 
repo
 
(architecture,
 
security,
 
coding
 
standards,
 
deployment)
 
 
●
 
Cursor
 
privacy
 
guide
 
(no
 
keys
 
in
 
prompts;
 
what’s
 
allowed
 
to
 
be
 
shared)
 
 
●
 
Optional:
 
Cursor
 
MCP
 
plan
 
(start
 
read-only;
 
minimal
 
servers;
 
document
 
access)
 
 
 
8)
 
Research
 
checklist
 
(outputs
 
+
 
decisions
 
unlocked)
 

## Page 16

A)
 
Browser
 
automation
 
●
 
Research:
 
Playwright
 
vs
 
Selenium
 
→
 
Output:
 
1-page
 
decision
 
note
 
→
 
Unlocks:
 
framework
 
choice
 
 
●
 
Research:
 
DOM/AX
 
tree
 
vs
 
screenshots
 
→
 
Output:
 
observation
 
stack
 
spec
 
→
 
Unlocks:
 
how
 
Jarvis
 
“sees”
 
 
●
 
Research:
 
iframes/shadow
 
DOM/SPAs
 
→
 
Output:
 
known
 
issues
 
playbook
 
→
 
Unlocks:
 
fallback
 
rules
 
 
●
 
Research:
 
captcha
 
handling
 
→
 
Output:
 
policy
 
snippet
 
→
 
Unlocks:
 
takeover
 
flow
 
 
●
 
Research:
 
ToS
 
boundaries
 
→
 
Output:
 
allow/blocked
 
matrix
 
→
 
Unlocks:
 
guardrails
 
+
 
confirm
 
gates
 
 
B)
 
Windows
 
local
 
agent
 
●
 
Research:
 
UIA
 
vs
 
input
 
vs
 
hybrid
 
→
 
Output:
 
decision
 
doc
 
→
 
Unlocks:
 
OS
 
method
 
 
●
 
Research:
 
packaging/updates
 
→
 
Output:
 
deployment
 
plan
 
→
 
Unlocks:
 
how
 
you
 
ship
 
companion
 
 
●
 
Research:
 
secure
 
pairing/revoke
 
→
 
Output:
 
pairing
 
spec
 
→
 
Unlocks:
 
device
 
safety
 
model
 
 
●
 
Research:
 
secrets
 
stay
 
local
 
→
 
Output:
 
policy
 
doc
 
→
 
Unlocks:
 
trust
 
boundaries
 
 
C)
 
Live
 
sessions
 
●
 
Research:
 
WebRTC
 
signaling
 
approach
 
→
 
Output:
 
architecture
 
diagram
 
→
 
Unlocks:
 
live
 
plumbing
 
 
●
 
Research:
 
streaming
 
STT
 
provider
 
→
 
Output:
 
comparison
 
sheet
 
→
 
Unlocks:
 
transcription
 
strategy
 
 

## Page 17

●
 
Research:
 
streaming
 
TTS
 
+
 
barge-in
 
→
 
Output:
 
voice
 
interaction
 
spec
 
→
 
Unlocks:
 
natural
 
conversation
 
 
●
 
Research:
 
frame
 
sampling
 
rate
 
vs
 
cost
 
→
 
Output:
 
budget
 
table
 
→
 
Unlocks:
 
defaults/cost
 
control
 
 
●
 
Research:
 
retention/recording
 
policy
 
→
 
Output:
 
privacy
 
policy
 
→
 
Unlocks:
 
consent
 
+
 
storage
 
rules
 
 
D)
 
Security/privacy/retention
 
●
 
Research:
 
retention
 
model
 
→
 
Output:
 
retention
 
table
 
→
 
Unlocks:
 
delete/export
 
features
 
 
●
 
Research:
 
redaction/logging
 
→
 
Output:
 
logging
 
policy
 
→
 
Unlocks:
 
safe
 
debugging
 
 
●
 
Research:
 
permission
 
tiers
 
→
 
Output:
 
permissions
 
matrix
 
→
 
Unlocks:
 
Suggest/Assist/Agent
 
behavior
 
 
E)
 
Cost/performance
 
●
 
Research:
 
model
 
routing
 
fast
 
vs
 
best
 
→
 
Output:
 
routing
 
policy
 
→
 
Unlocks:
 
predictable
 
spend/latency
 
 
●
 
Research:
 
queue
 
+
 
retry
 
design
 
→
 
Output:
 
job
 
plan
 
→
 
Unlocks:
 
reliable
 
ingestion
 
 
●
 
Research:
 
context
 
management
 
→
 
Output:
 
context
 
policy
 
→
 
Unlocks:
 
long-chat
 
stability
 
 
F)
 
Evaluation/QA
 
●
 
Research:
 
eval
 
pack
 
→
 
Output:
 
prompts
 
+
 
rubric
 
→
 
Unlocks:
 
regression
 
testing
 
 
●
 
Research:
 
agent
 
safety
 
tests
 
→
 
Output:
 
safety
 
suite
 
→
 
Unlocks:
 
guardrails
 
proof
 
 
●
 
Research:
 
verification
 
library
 
→
 
Output:
 
rules
 
library
 
→
 
Unlocks:
 
reliable
 
automation
 
 

## Page 18

G)
 
UX
 
●
 
Research:
 
plan
 
preview/approvals
 
UX
 
→
 
Output:
 
UX
 
spec
 
→
 
Unlocks:
 
safe
 
agent
 
control
 
experience
 
 
●
 
Research:
 
live
 
indicator
 
+
 
panic
 
stop
 
UX
 
→
 
Output:
 
indicator
 
spec
 
→
 
Unlocks:
 
safety
 
+
 
clarity
 
 
 
Want
 
me
 
to
 
include
 
your
 
uploaded
 
“plan
 
images”
 
too?
 
Since
 
downloads
 
are
 
failing,
 
the
 
easiest
 
way
 
is:
 
●
 
You
 
save
 
this
 
message
 
as
 
a
 
PDF
 
(steps
 
above)
 
 
●
 
Then
 
in
 
Word/Google
 
Docs,
 
insert
 
your
 
images
 
afterward
 
and
 
export
 
again
 
 
If
 
you
 
tell
 
me
 
what
 
device
 
you’re
 
using
 
right
 
now
 
(ChatGPT
 
iOS
 
app
 
vs
 
Safari
 
vs
 
desktop
 
browser),
 
I’ll
 
give
 
you
 
the
 
exact
 
click-by-click
 
path
 
that
 
works
 
on
 
that
 
device.
 
 
