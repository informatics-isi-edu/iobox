SELECT DISTINCT 
ID,
BiomassProdBatchID,
BiomassProduced,
CellEquivmL,
Date,
Disabled,
FlaskVolume,
LastUpdate,
Name,
Notes,
NumberWashes,
SrcCellDensity,
SrcCellDensityExp,
StdCellDensity,
StdCellDensityExp,
UserDate,
UserID,
Volume,
1 AS site_prov
    FROM  MembranePrep 
          WHERE BiomassProdBatchID in (SELECT id from BiomassProdBatch) 
                AND UserID in (SELECT id from userlist) ;  
