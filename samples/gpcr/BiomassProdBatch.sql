SELECT * FROM BiomassProdBatch WHERE ConstructID in (SELECT id from construct) 
    AND userid in (SELECT id from userlist) 
    AND VirusProdBatchID in (SELECT id FROM virusproduction) ;
