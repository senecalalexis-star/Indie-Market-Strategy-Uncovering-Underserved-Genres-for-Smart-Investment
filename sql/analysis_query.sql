-- =============================================
--ANALYSIS : Indie Market Strategy Uncovering Underserved Genres for Smart Investment
--Objective : Guiding Raw Digital’s investment strategy 
-- =============================================

--MASTER QUERY:

--Use For :
--Section 1 : Identifying which genre the greatest revenue upside.
--Section 3 : Identifying which genre offer the strongest engagement.
SELECT 
    gi.game_id, 
    gi.reviews, 
	pt.median_playtime_minutes,
    t.tag_name,
	gi.price
FROM game_info AS gi
LEFT JOIN game_tag AS gt ON gt.game_id = gi.game_id
LEFT JOIN tag AS t ON t.tag_id = gt.tag_id
LEFT JOIN play_time AS pt ON pt.game_id = gi.game_id
WHERE gt.game_id IN (
      SELECT game_id
      FROM game_tag
      WHERE tag_id = 4 --Only keep indie game 
)
AND t.is_game_genre = TRUE --Only game tag for game genre
AND gi.release BETWEEN '2024-01-01' AND '2025-12-31' --Only keep relevant date
GROUP BY gi.game_id, gi.reviews,pt.median_playtime_minutes, t.tag_name, gi.price
ORDER BY game_id;


--Use For Section 2 : Identifying which genres are not oversaturated.

SELECT 
    gi.game_id,
    t.tag_name
FROM game_info AS gi
LEFT JOIN game_tag AS gt ON gt.game_id = gi.game_id
LEFT JOIN tag AS t ON t.tag_id = gt.tag_id
WHERE gt.game_id IN (
      SELECT game_id
      FROM game_tag
      WHERE tag_id = 4
)
AND t.is_game_genre = TRUE
AND gi.release BETWEEN '2024-01-01' AND '2025-12-31'
GROUP BY gi.game_id, t.tag_name
ORDER BY game_id;