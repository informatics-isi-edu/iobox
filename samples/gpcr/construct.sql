SELECT 
C.ID,
C.CleavageSite,
C.Comments,
C.DateRegistered,
C.ExptAASeq,
C.ExptMWNum,
C.ExptNucSeq,
C.host,
C.Insertion,
C.IsDisabled,
C.LastUpdate,
C.MicroscreenComments,
C.MicroscreenScore,
C.Mutations,
C.Name,
C.Organism,
C.ParentID,
C.Status,
C.Strain,
C.TagCterm,
C.TagNterm,
C.Target,
C.Truncations,
C.Updated,
C.Vector,
1 AS site_prov,
CASE WHEN T.permit=1 THEN 'true' ELSE 'false' END AS shared
     FROM  construct C
     JOIN  target T ON (C.target=T.id) 
       WHERE T.permit=1;



