// As-of-date beneficial ownership resolution
MATCH p=(owner)-[rels:OWNS*1..8]->(target:Entity {entity_id: $entity_id})
WHERE ALL(r IN rels WHERE r.effective_from <= date($as_of_date) AND (r.effective_to IS NULL OR r.effective_to >= date($as_of_date)))
RETURN owner, target, rels,
       reduce(pct = 1.0, r IN rels | pct * (toFloat(r.ownership_percentage) / 100.0)) AS cumulative_ownership_fraction
ORDER BY cumulative_ownership_fraction DESC
LIMIT 25;

// Provenance inspection for conflicting disclosures
MATCH (owner)-[r:OWNS]->(target:Entity {entity_id: $entity_id})
RETURN owner, r.disclosure_source, r.disclosure_date, r.ownership_percentage
ORDER BY r.disclosure_date DESC;
