ALTER TABLE anime_data ADD PRIMARY KEY (anime_id);

DELETE FROM user_ratings 
WHERE anime_id NOT IN (SELECT anime_id FROM anime_data);

ALTER TABLE user_ratings ADD CONSTRAINT fk_anime FOREIGN KEY (anime_id) REFERENCES anime_data (anime_id);