SELECT 
B.ID,
B.Additives_Conditions,
B.AmountRemaining,
B.Block,
B.CellCount,
B.CellViability,
B.ConstructID,
B.CreatedBy,
B.CurrentStatus,
B.Date,
B.Disabled,
B.EndDate,
B.EndUser,
B.FLAGpdead,
B.FLAGpdead_alt,
B.FLAGplive,
B.FLAGplive_alt,
B.FlaskVolume,
B.Infected_Cell_Count,
B.Infected_Cell_Viability,
B.LastUpdate,
B.MediaLot,
B.ModifiedBy,
B.MOI,
B.Name,
B.nonexpdead,
B.nonexpdead_alt,
B.nonexplive,
B.nonexplive_alt,
B.Notes,
B.P0,
B.Passage,
B.percent_infected_gp64,
B.percent_surface,
B.percent_tx100,
B.PickedUpBy,
B.RequestType,
B.StartDate,
B.Status,
B.surf_l_1,
B.surf_l_1_alt,
B.surf_l_2,
B.surf_l_2_alt,
B.surf_mu_1,
B.surf_mu_1_alt,
B.surf_mu_2,
B.surf_mu_2_alt,
B.surf_s,
B.surf_s_alt,
B.Target,
B.TF,
B.TF_alt,
B.tot_l_1,
B.tot_l_1_alt,
B.tot_l_2,
B.tot_l_2_alt,
B.tot_mu_1,
B.tot_mu_1_alt,
B.tot_mu_2,
B.tot_mu_2_alt,
B.tot_s,
B.tot_s_alt,
B.UserID,
B.VirusPassage,
B.VirusProdBatchID, 
B.Volume,
B.WellBag,
B.xmean_surface,
B.xmean_tx100,
1 AS site_prov,
CASE WHEN T.permit=1 THEN 'true' ELSE 'false' END AS shared 
    FROM  BiomassProdBatch B 
    JOIN  construct C ON (B.constructid=C.id)
    JOIN  target T ON (C.target=T.id)
      WHERE T.permit=1
        AND userid in (SELECT id from userlist) 
        AND VirusProdBatchID in (SELECT id FROM virusproduction) ;

