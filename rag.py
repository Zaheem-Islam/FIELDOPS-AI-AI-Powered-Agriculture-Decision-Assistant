KNOWLEDGE = [
    {
        "keywords": ["wheat", "flowering", "moisture"],
        "text": "Wheat at flowering is a water-sensitive stage; low soil moisture during this stage warrants closer water-stress monitoring."
    },
    {
        "keywords": ["wheat", "rainfall"],
        "text": "When recent and expected rainfall are limited, irrigation decisions should consider crop stage and current soil moisture together."
    },
    {
        "keywords": ["soil", "moisture"],
        "text": "Soil moisture should be interpreted together with crop stage, recent rainfall and expected weather rather than as an isolated value."
    },
    {
        "keywords": ["image", "disease"],
        "text": "Visible leaf symptoms are suitable for preliminary screening only; field inspection and validated diagnosis are required before treating a disease."
    }
]

def retrieve_guidance(crop, stage, moisture, rainfall):
    query = f"{crop} {stage} moisture rainfall".lower()
    scored = []
    for item in KNOWLEDGE:
        score = sum(1 for k in item["keywords"] if k in query)
        if score:
            scored.append((score, item["text"]))
    scored.sort(reverse=True)
    return [x[1] for x in scored[:3]] or [
        "General guidance: interpret crop condition using multiple evidence sources and verify consequential actions in the field."
    ]
