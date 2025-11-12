WITH target_club AS (
    SELECT id_clu, name FROM clubs WHERE name = 'Club 1'
)
SELECT
    p.name,
    AVG(pgs.assists)::numeric(10,2) AS average_assists_per_game
FROM player AS p
JOIN target_club AS tc ON p.current_club_id = tc.id_clu
JOIN player_game_stats AS pgs ON p.id_pla = pgs.id_pla
WHERE EXISTS (
    SELECT 1
    FROM game_participant AS gp
    WHERE gp.id_gam = pgs.id_gam
      AND gp.participant_type = 'Club'
      AND gp.participant_id = tc.id_clu
)
GROUP BY p.id_pla, p.name
ORDER BY average_assists_per_game DESC
LIMIT 1;
