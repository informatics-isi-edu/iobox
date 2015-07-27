SELECT * FROM MembranePrep where BiomassProdBatchID in (SELECT id from BiomassProdBatch) 
          AND UserID in (SELECT id from userlist) ;
