SELECT
    c.name,
    AVG(p.height) AS average_height
FROM clubs AS c
JOIN player AS p ON c.id_clu = p.current_club_id
WHERE p.height IS NOT NULL
GROUP BY c.id_clu, c.name
ORDER BY average_height DESC
LIMIT 1;
