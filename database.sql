-- MySQL dump 9.11
--
-- Host: localhost    Database: tp
-- ------------------------------------------------------
-- Server version	4.0.20-log

--
-- Table structure for table `board`
--

DROP TABLE IF EXISTS `board`;
CREATE TABLE `board` (
  `id` bigint(20) NOT NULL default '0',
  `name` tinyblob NOT NULL,
  `desc` blob NOT NULL,
  PRIMARY KEY  (`id`)
) TYPE=MyISAM;

--
-- Dumping data for table `board`
--

INSERT INTO `board` VALUES (11,'Private message board for t','This board is used so that stuff you own (such as fleets and planets) can inform you of what is happening in the universe. ');

--
-- Table structure for table `message`
--

DROP TABLE IF EXISTS `message`;
CREATE TABLE `message` (
  `id` bigint(20) NOT NULL auto_increment,
  `bid` bigint(20) NOT NULL default '0',
  `slot` bigint(20) NOT NULL default '0',
  `subject` tinyblob NOT NULL,
  `body` blob NOT NULL,
  PRIMARY KEY  (`id`)
) TYPE=MyISAM;

--
-- Dumping data for table `message`
--


--
-- Table structure for table `object`
--

DROP TABLE IF EXISTS `object`;
CREATE TABLE `object` (
  `id` bigint(20) NOT NULL auto_increment,
  `type` varchar(255) NOT NULL,
  `name` tinyblob NOT NULL,
  `size` bigint(20) NOT NULL default '0',
  `posx` bigint(20) NOT NULL default '0',
  `posy` bigint(20) NOT NULL default '0',
  `posz` bigint(20) NOT NULL default '0',
  `velx` bigint(20) NOT NULL default '0',
  `vely` bigint(20) NOT NULL default '0',
  `velz` bigint(20) NOT NULL default '0',
  `parent` bigint(20) NOT NULL default '-1',
  `extra` blob NOT NULL,
  PRIMARY KEY  (`id`)
) TYPE=MyISAM;

--
-- Dumping data for table `object`
--

INSERT INTO `object` VALUES (-1,'sobjects.Universe','The Universe',100000000000,0,0,0,0,0,0,-1,'(dp0\nS\'turn\'\np1\nI0\ns.');
INSERT INTO `object` VALUES (25,'sobjects.Galaxy','The Milky Way',10000000000,0,0,-6000,0,0,1000,0,'(dp0\n.');
INSERT INTO `object` VALUES (26,'sobjects.System','The Sol Terra System',1400000,3000000000,2000000000,0,-1500000,1500000,0,25,'(dp0\n.');
INSERT INTO `object` VALUES (27,'sobjects.System','The Alpha Centauri System',800000,-1500000000,1500000000,0,-1000000,-1000000,0,25,'(dp0\n.');
INSERT INTO `object` VALUES (28,'sobjects.System','Sirius System',2000000,-250000000,-4000000000,0,2300000,0,0,25,'(dp0\n.');
INSERT INTO `object` VALUES (52,'sobjects.System','t\'s System',1630922,67203857,-9289417568,-7649254180,0,0,0,0,'(dp0\n.');
INSERT INTO `object` VALUES (53,'sobjects.Planet','t\'s Homeworld',1000,67203857,-9289417568,-7649254180,0,0,0,52,'(dp0\nS\'owner\'\np1\nI11\ns.');
INSERT INTO `object` VALUES (54,'sobjects.Planet','Unknown planet',7207,67203857,-9289417568,-7649254180,0,0,0,52,'(dp0\nS\'owner\'\np1\nI11\ns.');
INSERT INTO `object` VALUES (55,'sobjects.Fleet','First Fleet',1,2147483647,-2147483647,-2147483647,0,0,0,0,'(dp0\nS\'owner\'\np1\nI11\nsS\'ships\'\np2\n(dp3\nI0\nI5\nssS\'damage\'\np4\n(dp5\ns.');

--
-- Table structure for table `order`
--

DROP TABLE IF EXISTS `order`;
CREATE TABLE `order` (
  `id` bigint(20) NOT NULL auto_increment,
  `type` varchar(255) NOT NULL,
  `oid` bigint(20) NOT NULL default '0',
  `slot` bigint(20) NOT NULL default '0',
  `turns` bigint(20) NOT NULL default '0',
  `extra` blob NOT NULL,
  PRIMARY KEY  (`id`)
) TYPE=MyISAM;

--
-- Dumping data for table `order`
--



--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` bigint(20) NOT NULL auto_increment,
  `username` tinyblob NOT NULL,
  `password` tinyblob NOT NULL,
  PRIMARY KEY  (`id`)
) TYPE=MyISAM;

--
-- Dumping data for table `user`
--

INSERT INTO `user` VALUES (11,'t','t');

UPDATE object SET id = 0 WHERE name='The Universe';
