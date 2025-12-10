/* Tables structurelles (ligues, championnats, entités) */

CREATE TABLE League (
    ID_Lea SERIAL PRIMARY KEY,
    League_ID VARCHAR(10) NOT NULL,
    Name VARCHAR(100) NOT NULL,
    Country VARCHAR(100) NOT NULL,
    Level VARCHAR(50) NOT NULL
);

CREATE TABLE Championship (
    ID_Cha SERIAL PRIMARY KEY,
    Championship_ID VARCHAR(10) NOT NULL,
    Name VARCHAR(100) NOT NULL,
    Year INT NOT NULL,
    Type VARCHAR(50) NOT NULL
);

CREATE TABLE Clubs (
    ID_Clu SERIAL PRIMARY KEY,
    Club_ID VARCHAR(10) NOT NULL,
    Name VARCHAR(100) NOT NULL,
    City VARCHAR(100) NOT NULL
);

CREATE TABLE Sponsor (
    ID_Spo SERIAL PRIMARY KEY,
    Sponsor_ID VARCHAR(10) NOT NULL,
    Company_name VARCHAR(100) NOT NULL,
    City VARCHAR(100),
    Contact_info VARCHAR(100)
);

CREATE TABLE National_team (
    ID_Nat SERIAL PRIMARY KEY,
    Team_ID VARCHAR(10) NOT NULL,
    Country VARCHAR(100) NOT NULL,
    Confederation VARCHAR(100)
);

CREATE TABLE Player (
    ID_Pla SERIAL PRIMARY KEY,
    Player_ID VARCHAR(10) NOT NULL,
    Name VARCHAR(100) NOT NULL,
    Date_of_birth DATE NOT NULL,
    Height DECIMAL(4, 2),
    Citizenship VARCHAR(50),
    Current_club_id INT,
    CONSTRAINT FK_Player_Club FOREIGN KEY (Current_club_id) REFERENCES Clubs (ID_Clu)
);

---
/* Tables de jeu et de statistiques (Structure principale corrigée) */

/* [MODIFIÉ] La table Game ne contient plus les scores ou le vainqueur */
CREATE TABLE Game (
    ID_Gam SERIAL PRIMARY KEY,
    Game_ID VARCHAR(10) NOT NULL,
    Game_date DATE NOT NULL,
    Location VARCHAR(100) NOT NULL,
    Game_type VARCHAR(50) NOT NULL,
    Season VARCHAR(50),
    ID_Lea INT,
    ID_Cha INT,
    CONSTRAINT FK_Game_League FOREIGN KEY (ID_Lea) REFERENCES League (ID_Lea),
    CONSTRAINT FK_Game_Championship FOREIGN KEY (ID_Cha) REFERENCES Championship (ID_Cha)
);

CREATE TABLE Game_Participant (
    ID_Gam INT NOT NULL,
    Participant_ID INT NOT NULL, -- Fait référence à ID_Clu OU ID_Nat
    Participant_Type VARCHAR(20) NOT NULL, -- 'Club' ou 'National'
    Score INT DEFAULT 0,
    Role VARCHAR(10), -- 'Home' ou 'Away'
    PRIMARY KEY (
        ID_Gam,
        Participant_ID,
        Participant_Type
    ),
    CONSTRAINT FK_GP_Game FOREIGN KEY (ID_Gam) REFERENCES Game (ID_Gam),
    CHECK (
        Participant_Type IN ('Club', 'National')
    )
);

/* [MODIFIÉ] Ajout des tirs tentés et des paniers à 2 points */
/* Résout les problèmes des requêtes 1, 2, et 5 */
CREATE TABLE PLAYER_GAME_STATS (
    ID_Gam INT NOT NULL,
    ID_Pla INT NOT NULL,
    ID_Stat SERIAL,

-- Statistiques complètes pour les calculs


Points_2pts_made INT DEFAULT 0,
    Points_2pts_attempted INT DEFAULT 0,
    Points_3pts_made INT DEFAULT 0,
    Points_3pts_attempted INT DEFAULT 0,
    Free_throws_made INT DEFAULT 0,
    Free_throws_attempted INT DEFAULT 0,

    Assists INT DEFAULT 0,
    Rebounds INT DEFAULT 0,
    Blocks INT DEFAULT 0,

    PRIMARY KEY (ID_Gam, ID_Pla),
    CONSTRAINT FK_PGS_Game FOREIGN KEY (ID_Gam)
        REFERENCES Game(ID_Gam),
    CONSTRAINT FK_PGS_Player FOREIGN KEY (ID_Pla)
        REFERENCES Player(ID_Pla)
);

---
/* Tables de liaison (Sponsors, Membres, etc.) */

CREATE TABLE Has_Sponsor_Club (
    ID_Clu INT NOT NULL,
    ID_Spo INT NOT NULL,
    PRIMARY KEY (ID_Clu, ID_Spo),
    CONSTRAINT FK_HSC_Club FOREIGN KEY (ID_Clu) REFERENCES Clubs (ID_Clu),
    CONSTRAINT FK_HSC_Sponsor FOREIGN KEY (ID_Spo) REFERENCES Sponsor (ID_Spo)
);

CREATE TABLE Has_Sponsor_Team (
    ID_Nat INT NOT NULL,
    ID_Spo INT NOT NULL,
    PRIMARY KEY (ID_Nat, ID_Spo),
    CONSTRAINT FK_HST_Team FOREIGN KEY (ID_Nat) REFERENCES National_team (ID_Nat),
    CONSTRAINT FK_HST_Sponsor FOREIGN KEY (ID_Spo) REFERENCES Sponsor (ID_Spo)
);

CREATE TABLE Member_of (
    ID_Pla INT NOT NULL,
    ID_Nat INT NOT NULL,
    Date_start DATE,
    Date_end DATE,
    PRIMARY KEY (ID_Pla, ID_Nat),
    CONSTRAINT FK_Member_Player FOREIGN KEY (ID_Pla) REFERENCES Player (ID_Pla),
    CONSTRAINT FK_Member_Team FOREIGN KEY (ID_Nat) REFERENCES National_team (ID_Nat)
);

/* Lie les équipes nationales inscrites à un championnat */
CREATE TABLE Participates_in (
    ID_Cha INT NOT NULL,
    ID_Nat INT NOT NULL,
    PRIMARY KEY (ID_Cha, ID_Nat),
    CONSTRAINT FK_Participates_Champ FOREIGN KEY (ID_Cha) REFERENCES Championship (ID_Cha),
    CONSTRAINT FK_Participates_Team FOREIGN KEY (ID_Nat) REFERENCES National_team (ID_Nat)
);

/* [NOUVEAU] Lie les clubs inscrits à une ligue */
CREATE TABLE Participates_in_League (
    ID_Lea INT NOT NULL,
    ID_Clu INT NOT NULL,
    PRIMARY KEY (ID_Lea, ID_Clu),
    CONSTRAINT FK_PIL_League FOREIGN KEY (ID_Lea) REFERENCES League (ID_Lea),
    CONSTRAINT FK_PIL_Club FOREIGN KEY (ID_Clu) REFERENCES Clubs (ID_Clu)
);

---
/* Index pour améliorer les performances */

CREATE INDEX IDX_Player_Club ON Player (Current_club_id);

CREATE INDEX IDX_Game_League ON Game (ID_Lea);

CREATE INDEX IDX_Game_Championship ON Game (ID_Cha);

CREATE INDEX IDX_GP_Participant ON Game_Participant (
    Participant_ID,
    Participant_Type
);

CREATE INDEX IDX_PGS_Player ON PLAYER_GAME_STATS (ID_Pla);

CREATE INDEX IDX_PGS_Game ON PLAYER_GAME_STATS (ID_Gam);

CREATE INDEX IDX_HSC_Sponsor ON Has_Sponsor_Club (ID_Spo);

CREATE INDEX IDX_HST_Sponsor ON Has_Sponsor_Team (ID_Spo);

CREATE INDEX IDX_Member_Team ON Member_of (ID_Nat);

CREATE INDEX IDX_Participates_Team ON Participates_in (ID_Nat);

CREATE INDEX IDX_PIL_Club ON Participates_in_League (ID_Clu);

/* [NOUVEAU] Index pour les recherches par nom (Optimisation) */
CREATE INDEX IDX_League_Name ON League (Name);

CREATE INDEX IDX_Championship_Name ON Championship (Name);

CREATE INDEX IDX_Clubs_Name ON Clubs (Name);

CREATE INDEX IDX_Player_Name ON Player (Name);

/* [NOUVEAU] Index pour les filtres de match fréquents */
CREATE INDEX IDX_Game_Type ON Game (Game_type);

CREATE INDEX IDX_Game_Season ON Game (Season);