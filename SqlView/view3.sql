CREATE OR REPLACE VIEW sponsors_of_national_teams AS
SELECT s.company_name, s.city, t.country
FROM
    Has_Sponsor_Team hst
    JOIN Sponsor s ON s.id_spo = hst.id_spo
    JOIN National_team t ON t.id_nat = hst.id_nat;
-- Note: 'TEAM_CHAMPIONSHIP_RESULTS' table does not exist, so we list sponsors of all national teams.