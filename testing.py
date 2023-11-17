import db_querying
print(db_querying.queryReviews(query='SELECT * FROM c WHERE IS_DEFINED(c.cluster) OFFSET 0 LIMIT 100'))