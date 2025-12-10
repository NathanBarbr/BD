CREATE OR REPLACE VIEW club_average_height AS
SELECT c.club_id, c.name AS club_name, AVG(p.height) AS avg_height
FROM Clubs c
    JOIN Player p ON p.current_club_id = c.id_clu
GROUP BY
    c.club_id,
    c.name;