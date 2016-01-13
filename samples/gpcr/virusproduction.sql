SELECT 
V.ID,
V.AdditivesConds,
V.Comments,
V.ConstructID,
V.Date,
V.DateINIT,
V.Disabled,
V.LastUpdate,
V.Location,
V.Notes,
V.OriginID,
V.P0comments,
V.P0date,
V.P0temp,
V.P0titer,
V.P1comments,
V.P1date,
V.P1temp,
V.P1titer,
V.P2comments,
V.P2date,
V.P2temp,
V.P2titer,
V.ParentPassageID,
V.Passage,
V.Status,
V.StockVolume,
V.StockVolumeUsed,
V.Titer,
V.TiterDate,
V.UserDate,
V.UserID,
1 AS site_prov,
CASE WHEN T.permit=1 THEN 'true' ELSE 'false' END AS shared
    FROM  virusproduction V 
    JOIN  construct C ON (V.constructid=C.id)
    JOIN  target T ON (C.target=T.id)
      WHERE T.permit=1
        AND ConstructID in (SELECT id FROM construct) 
        AND userid in (SELECT id FROM userlist) ; 
