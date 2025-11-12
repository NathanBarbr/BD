WITH world_final_participants AS (
    SELECT
        g.id_gam,
        gp.participant_id,
        gp.score,
        RANK() OVER (PARTITION BY g.id_gam ORDER BY gp.score DESC) AS score_rank
    FROM game AS g
    JOIN championship AS c ON g.id_cha = c.id_cha
    JOIN game_participant AS gp ON g.id_gam = gp.id_gam
    WHERE
        c.name = 'World Championship'
        AND g.game_type = 'Final'
        AND gp.participant_type = 'National'
), world_final_winners AS (
    SELECT DISTINCT participant_id AS winning_team_id
    FROM world_final_participants
    WHERE score_rank = 1
)
SELECT
    s.company_name,
    COUNT(DISTINCT hst.id_nat) AS sponsored_winners_count
FROM sponsor AS s
JOIN has_sponsor_team AS hst ON s.id_spo = hst.id_spo
JOIN world_final_winners AS w ON hst.id_nat = w.winning_team_id
GROUP BY s.id_spo, s.company_name
ORDER BY sponsored_winners_count DESC
LIMIT 1;
