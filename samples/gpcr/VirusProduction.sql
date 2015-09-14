SELECT * FROM VirusProduction WHERE ConstructID in (SELECT id FROM construct) 
              AND userid in (SELECT id FROM userlist) ; 
