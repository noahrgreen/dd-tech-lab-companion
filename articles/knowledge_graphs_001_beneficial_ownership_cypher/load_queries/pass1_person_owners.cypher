
LOAD CSV WITH HEADERS FROM 'file:///ownership_synthetic.csv' AS row
WITH row WHERE row.owner_kind = 'Person'
MERGE (p:Person {uid: row.owner_uid})
  ON CREATE SET p.full_name = row.owner_full_name,
                p.jurisdiction = row.owner_jurisdiction,
                p.sanctioned = toBoolean(toInteger(row.owner_sanctioned)),
                p.created_at = datetime()
MERGE (e:Entity {uid: row.entity_uid})
  ON CREATE SET e.legal_name = row.entity_legal_name,
                e.jurisdiction = row.entity_jurisdiction,
                e.entity_type = row.entity_type,
                e.created_at = datetime()
MERGE (p)-[r:OWNS]->(e)
  SET r.percentage = toFloat(row.percentage),
      r.effective_date = date(row.effective_date),
      r.source_filing_ref = row.source_filing_ref;
