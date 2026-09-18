\# Lineage Trace Evaluation vs. Baseline LLM



\## Methodology \& Case Selection Criteria

\*\*Explicit Cherry-Picking Risk Statement:\*\* 

The 3–5 retrospective cases evaluated below were not randomly sampled. Cases were explicitly selected based on the availability of detailed public reporting and fact-check writeups that are comprehensive enough to verify our lineage reconstruction against. The goal is to prove structural capability against known ground-truth cascades, not to represent average daily platform traffic.



\---



\## Case 1: \[Insert Case Name/Topic]



\### 1. Baseline LLM (Single-Call Classification)

\*   \*\*Prompted with:\*\* \[Insert the raw text of the first claim in the cascade]

\*   \*\*Verdict:\*\* \[Insert True/False output]

\*   \*\*Limitation:\*\* The baseline evaluated the claim statically. It provided a factual verdict but could not identify who amplified it, how it was rewritten, or if the spread was coordinated.



\### 2. Lineage Trace Pipeline Output

\*   \*\*Specific Mutation Point:\*\* \[Describe the exact node/edge where the claim distortion occurred, e.g., "At hop 4, the qualifier 'allegedly' was stripped by Account X."]

\*   \*\*Coordination Signature:\*\* \[Describe the structural signal, e.g., "High timestamp burstiness flagged across 8 edges introducing the mutated version."]

\*   \*\*Topology Classification:\*\* \[Insert External Label: organic / coordinated / bot\_amplified] (\[Insert Internal Label: hub\_spoke / mesh / burst])

\*   \*\*Debunk-Lag Tracking:\*\*

&#x20;   \*   \*\*Time-to-debunk:\*\* \[X] hours

&#x20;   \*   \*\*Estimation Method:\*\* \[peak\_velocity OR fallback\_first\_seen] \*(Note: This field is required per Component 16 rules)\*

&#x20;   \*   \*\*Pre-debunk Reach:\*\* \[X] downstream nodes inherited the claim before the first debunker-role node appeared.



\### 3. Conclusion

\[Write a 2-3 sentence summary of what Lineage Trace's lineage graph revealed that the standard consumer verdict baseline missed entirely.]



\---



\## Case 2: \[Insert Case Name/Topic]

\*(Duplicate template structure above for cases 2 through 5)\*

