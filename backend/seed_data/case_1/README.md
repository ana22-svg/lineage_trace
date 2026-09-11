\# Case 1: The "10 to 100" Exaggeration Cascade



\*\*Origin\*\*: Curated retrospective case based on standard claim mutation patterns.

\*\*Objective\*\*: Demonstrate the complete pipeline tracking a factual drift (a number inflating from 10 to 100) and catching a coordinated amplification burst.



\*\*Key Features to Test:\*\*

\- \*\*Mutation\*\*: The core claim mutates at node 3, changing "10 workers" to "100 workers."

\- \*\*Coordination\*\*: Nodes 3, 4, and 5 represent a bot-amplified burst, identifiable by tight timestamp clustering and low `author\_account\_age\_days` (seed-only signal).

\- \*\*Debunk Lag\*\*: Node 6 enters with a `debunker` role to trigger the debunk-lag tracker.

