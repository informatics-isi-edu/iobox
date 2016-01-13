SELECT  
  T.id,
  T.lastupdate,
  T.name,
  1 AS site_prov,
  T.targetid,
  CASE WHEN T.permit=1 THEN 1 ELSE 0 END AS permit,
  CASE WHEN T.permit=1 THEN 'true' ELSE 'false' END AS shared
     FROM  target T  WHERE permit=1;
     
