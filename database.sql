DROP DATABASE IF EXISTS tp;
CREATE DATABASE tp;
USE tp;
-- MySQL dump 10.9
--
-- Host: localhost    Database: tp
-- ------------------------------------------------------
-- Server version	4.1.8a-Debian_6-log

--
-- Table structure for table `board`
--

DROP TABLE IF EXISTS `board`;
CREATE TABLE `board` (
  `id` bigint(20) NOT NULL default '0',
  `name` tinyblob NOT NULL,
  `desc` blob NOT NULL,
  `time` bigint(20) NOT NULL default '0',
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `board`
--


--
-- Table structure for table `category`
--

DROP TABLE IF EXISTS `category`;
CREATE TABLE `category` (
  `id` bigint(20) NOT NULL auto_increment,
  `name` tinytext NOT NULL,
  `desc` text,
  `time` bigint(20) NOT NULL default '0',
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `category`
--

INSERT INTO `category` VALUES (1,'Misc','Things which don\'t fit into any specific category.',0);

--
-- Table structure for table `component`
--

DROP TABLE IF EXISTS `component`;
CREATE TABLE `component` (
  `id` bigint(20) NOT NULL auto_increment,
  `base` bigint(20) default NULL,
  `name` tinytext NOT NULL,
  `desc` text NOT NULL,
  `language` tinyblob,
  `time` bigint(20) NOT NULL default '0',
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `component`
--

INSERT INTO `component` VALUES 	(1,0,'Generic Base Component A','A very generic component that can be used for almost anything.',NULL,0),
								(2,0,'Generic Base Component B','A very generic component that can be used anywhere Component A can\'t be.',NULL,0),
								(3,0,'Generic Base Component C','A very generic component that can be used inplace of Component B can\'t be.',NULL,0),
								(4,0,'Generic Hull','A very generic hull component that can have Generic Base Components added to it.','((I1\nI2\nI3\ntp0\n(I1\nI6\nI2\ntp1\n(I4\nI0\nI0\ntp2\n(I1\nI3\nI1\ntp3\n(I3\nI0\nI0\ntp4\ntp5\n.', 0);

--
-- Table structure for table `component_category`
--

DROP TABLE IF EXISTS `component_category`;
CREATE TABLE `component_category` (
  `component` bigint(20) NOT NULL default '0',
  `category` bigint(20) NOT NULL default '0',
  PRIMARY KEY  (`component`,`category`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `component_category`
--

INSERT INTO `component_category` VALUES (1,1),(2,1),(3,1),(4,1);

--
-- Table structure for table `component_component`
--

DROP TABLE IF EXISTS `component_component`;
CREATE TABLE `component_component` (
  `container` bigint(20) NOT NULL default '0',
  `component` bigint(20) NOT NULL default '0',
  PRIMARY KEY  (`container`,`component`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `component_component`
--


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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `message`
--


--
-- Table structure for table `object`
--

DROP TABLE IF EXISTS `object`;
CREATE TABLE `object` (
  `id` bigint(20) NOT NULL auto_increment,
  `type` varchar(255) NOT NULL default '',
  `name` tinyblob NOT NULL,
  `size` bigint(20) NOT NULL default '0',
  `posx` bigint(20) NOT NULL default '0',
  `posy` bigint(20) NOT NULL default '0',
  `posz` bigint(20) NOT NULL default '0',
  `velx` bigint(20) NOT NULL default '0',
  `vely` bigint(20) NOT NULL default '0',
  `velz` bigint(20) NOT NULL default '0',
  `parent` bigint(20) NOT NULL default '-1',
  `time` bigint(20) NOT NULL default '0',
  `extra` blob NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `object`
--

INSERT INTO `object` VALUES (-1,'sobjects.Universe','The Universe',100000000000,0,0,0,0,0,0,-1,0,'(dp0\nS\'turn\'\np1\nI0\ns.'),
							(1,'sobjects.Galaxy','The Milky Way',10000000000,0,0,-6000,0,0,1000,0,0,'(dp0\n.');

--
-- Table structure for table `order`
--

DROP TABLE IF EXISTS `order`;
CREATE TABLE `order` (
  `id` bigint(20) NOT NULL auto_increment,
  `type` varchar(255) NOT NULL default '',
  `oid` bigint(20) NOT NULL default '0',
  `slot` bigint(20) NOT NULL default '0',
  `worked` bigint(20) NOT NULL default '0',
  `extra` blob NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

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
  `time` bigint(20) NOT NULL default '0',
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `user`
--

INSERT INTO `user` VALUES (1,'admin@tp','adminpassword', 0);


--
-- Table structure for table `resource`
--

DROP TABLE IF EXISTS `resource`;
CREATE TABLE `resource` (
  `id` bigint(20) NOT NULL auto_increment,
  `namesingular` tinytext NOT NULL,
  `nameplural` tinytext NOT NULL,
  `unitsingular` tinytext NOT NULL,
  `unitplural` tinytext NOT NULL,
  `desc` text,
  `weight` bigint(20) NOT NULL default '0',
  `size` bigint(20) NOT NULL default '0',
  `time` bigint(20) NOT NULL default '0',
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


--
-- Table structure for table `permission`
--

-- DROP TABLE IF EXISTS `permission`;
-- CREATE TABLE `permission` (
--   `id` bigint(20) NOT NULL auto_increment,
--   `name` tinyblob NOT NULL,
--   PRIMARY KEY  (`id`)
-- ) ENGINE=InnoDB DEFAULT CHARSET=latin1;


UPDATE object SET id = 0 WHERE name='The Universe';
