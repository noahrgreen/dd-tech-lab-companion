MATCH p=(person:Person)-[:OWNS*1..6]->(entity:Entity)
RETURN person, entity, p
LIMIT 25;
