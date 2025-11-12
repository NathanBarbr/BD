WITH euroleague_finals AS (
    SELECT g.id_gam
    FROM game AS g
    JOIN league AS l ON g.id_lea = l.id_lea
    WHERE l.name = 'Euroleague'
      AND g.game_type = 'Final'
), final_winners AS (
    SELECT DISTINCT
        gp.id_gam,
        gp.participant_id AS winning_club_id
    FROM game_participant AS gp
    JOIN euroleague_finals AS ef ON gp.id_gam = ef.id_gam
    WHERE gp.participant_type = 'Club'
      AND gp.score = (
          SELECT MAX(gp2.score)
          FROM game_participant AS gp2
          WHERE gp2.id_gam = gp.id_gam
            AND gp2.participant_type = 'Club'
      )
)
SELECT
    c.name,
    COUNT(fw.winning_club_id) AS times_won
FROM clubs AS c
JOIN final_winners AS fw ON c.id_clu = fw.winning_club_id
GROUP BY c.id_clu, c.name
HAVING COUNT(fw.winning_club_id) > 3
ORDER BY times_won DESC;
