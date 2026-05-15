import csv
import random

random.seed(42)

PERSON_COUNT = 25
ENTITY_COUNT = 75
SANCTIONED_PERSONS = {"P-0001", "P-0002"}
TARGET_ENTITY = "E-0042"

jurisdictions = ["US-DE", "US-NY", "KY", "BVI", "LU", "SG"]

persons = [
    {
        "uid": f"P-{i:04d}",
        "name": f"Person {i:02d}",
        "jurisdiction": random.choice(jurisdictions),
        "sanctioned": 1 if f"P-{i:04d}" in SANCTIONED_PERSONS else 0,
    }
    for i in range(1, PERSON_COUNT + 1)
]

entities = [
    {
        "uid": f"E-{i:04d}",
        "name": f"Entity {i:03d}",
        "jurisdiction": random.choice(jurisdictions),
        "entity_type": random.choice(["OperatingCo", "HoldCo", "SPV"]),
    }
    for i in range(1, ENTITY_COUNT + 1)
]

rows = []
for entity in entities:
    owner_count = random.choice([1, 2, 3])
    weights = [random.random() for _ in range(owner_count)]
    total = sum(weights)
    pct_list = [round(w / total, 4) for w in weights]
    pct_list[-1] = round(1.0 - sum(pct_list[:-1]), 4)
    for pct in pct_list:
        owner_kind = random.choice(["Person", "Entity"])
        owner_pool = persons if owner_kind == "Person" else entities
        owner = random.choice(owner_pool)
        if owner["uid"] == entity["uid"]:
            continue
        rows.append({
            "owner_kind": owner_kind,
            "owner_uid": owner["uid"],
            "owner_full_name": owner["name"],
            "owner_jurisdiction": owner["jurisdiction"],
            "owner_sanctioned": owner.get("sanctioned", 0),
            "entity_uid": entity["uid"],
            "entity_legal_name": entity["name"],
            "entity_jurisdiction": entity["jurisdiction"],
            "entity_type": entity["entity_type"],
            "percentage": pct,
            "effective_date": "2024-12-31",
            "source_filing_ref": f"SYNTH-{entity['uid']}-2024-001",
        })

cascade_holders = [
    ("P-0001", "Entity 042 HoldCo", "E-0042", 0.26),
    ("P-0002", "Entity 042 Upper HoldCo", "E-0066", 0.24),
    ("E-0066", "Entity 042 HoldCo", "E-0042", 0.30),
]
for owner_uid, owner_name, entity_uid, pct in cascade_holders:
    rows.append({
        "owner_kind": "Person" if owner_uid.startswith("P-") else "Entity",
        "owner_uid": owner_uid,
        "owner_full_name": owner_name if owner_uid.startswith("E-") else next(p["name"] for p in persons if p["uid"] == owner_uid),
        "owner_jurisdiction": "US-DE",
        "owner_sanctioned": 1 if owner_uid in SANCTIONED_PERSONS else 0,
        "entity_uid": entity_uid,
        "entity_legal_name": next(e["name"] for e in entities if e["uid"] == entity_uid),
        "entity_jurisdiction": "US-DE",
        "entity_type": next(e["entity_type"] for e in entities if e["uid"] == entity_uid),
        "percentage": pct,
        "effective_date": "2024-12-31",
        "source_filing_ref": f"SYNTH-{entity_uid}-2024-001",
    })

with open("ownership_synthetic.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} ownership rows. TARGET_ENTITY = {TARGET_ENTITY!r}")
