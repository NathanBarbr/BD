CREATE OR REPLACE VIEW top_national_team_scorers AS
SELECT p.player_id, p.name, SUM(
        2 * pgs.points_2pts_made + 3 * pgs.points_3pts_made + pgs.free_throws_made
    ) AS total_points
FROM
    Player p
    JOIN Player_Game_Stats pgs ON p.id_pla = pgs.id_pla
    JOIN Game g ON g.id_gam = pgs.id_gam
WHERE
    g.game_type IN ('Group Stage', 'Final') -- Adjusted to match existing data
GROUP BY
    p.player_id,
    p.name;