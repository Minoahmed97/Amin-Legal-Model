# Evaluation plan

Evaluate on reviewed Egyptian-law tasks with held-out examples.

Core dimensions:
- Factual fidelity to supplied records.
- Correct identification of parties and procedural posture.
- Accuracy of statutory and judgment citations.
- Separation of facts, evidence, allegations, and inference.
- Issue spotting, counterarguments, and missing-evidence detection.
- Arabic legal drafting quality and terminology.
- Calibration: explicit uncertainty and abstention when sources are insufficient.
- Privacy leakage and resistance to prompt injection in uploaded documents.

Every legal citation must be checked against an authoritative source. Do not score fluent unsupported output as correct.


## Strategic decision benchmark

Every case scenario should be independently annotated by at least two Egyptian lawyers and adjudicated when they disagree. Record the procedural stage, client role, service dates, mandatory response obligations, limitation/forfeiture hazards, missing evidence, opponent's strongest point, supported response points, and the actual decision context.

Score separately:
- Whether the system detects a legally mandatory response or deadline risk.
- Whether it avoids tactical silence where silence may waive or prejudice a right.
- Whether it avoids unnecessary broad replies that reveal strategy or cure opponent omissions.
- Whether it distinguishes supported points from allegations and unverified theories.
- Whether its choice of targeted response, comprehensive brief, evidence request, or no substantive reply is justified.
- Whether it states conditions that would change the recommendation.

Do not reward a correct recommendation reached by invented facts, unsupported legal rules, or hindsight. The current strategy endpoint is a transparent heuristic and must not be represented as expert judgment until this benchmark is completed.
