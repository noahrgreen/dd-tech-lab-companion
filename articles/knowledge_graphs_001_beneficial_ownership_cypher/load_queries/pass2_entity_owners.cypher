
LOAD CSV WITH HEADERS FROM 'file:///ownership_synthetic.csv' AS row
WITH row WHERE row.owner_kind = 'Entity'
MERGE (owner:Entity {uid: row.owner_uid})
  ON CREATE SET owner.legal_name = row.owner_full_name,
                owner.jurisdiction = row.owner_jurisdiction,
                owner.created_at = datetime()
MERGE (e:Entity {uid: row.entity_uid})
  ON CREATE SET e.legal_name = row.entity_legal_name,
                e.jurisdiction = row.entity_jurisdiction,
                e.entity_type = row.entity_type,
                e.created_at = datetime()
MERGE (owner)-[r:OWNS]->(e)
  SET r.percentage = toFloat(row.percentage),
      r.effective_date = date(row.effective_date),
      r.source_filing_ref = row.source_filing_ref;
