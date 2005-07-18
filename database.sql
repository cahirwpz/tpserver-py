CREATE DATABASE tp;
USE tp;
-- MySQL dump 10.9
--
-- Host: localhost    Database: tp
-- ------------------------------------------------------
-- Server version	4.1.12-Debian_1-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

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

INSERT INTO `category` VALUES (1,'Misc','Things which don\'t fit into any specific category.',0),(2,'Physical','Physical properties of an object.',0);

--
-- Table structure for table `component`
--

DROP TABLE IF EXISTS `component`;
CREATE TABLE `component` (
  `id` bigint(20) NOT NULL auto_increment,
  `name` tinytext NOT NULL,
  `desc` text NOT NULL,
  `requirements` tinyblob,
  `time` bigint(20) NOT NULL default '0',
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `component`
--

INSERT INTO `component` VALUES (1,'Generic Base Component A','A very generic component that can be used for almost anything.','',0),(2,'Generic Base Component B','A very generic component that can be used anywhere Component A can\'t be.','',0),(3,'Generic Base Component C','A very generic component that can be used inplace of Component B can\'t be.','',0),(4,'Generic Hull','A very generic hull component that can have Generic Base Components added to it.','',0);

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
-- Table structure for table `component_property`
--

DROP TABLE IF EXISTS `component_property`;
CREATE TABLE `component_property` (
  `component` bigint(20) NOT NULL default '0',
  `property` bigint(20) NOT NULL default '0',
  `value` tinyblob NOT NULL,
  PRIMARY KEY  (`component`,`property`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `component_property`
--


--
-- Table structure for table `design`
--

DROP TABLE IF EXISTS `design`;
CREATE TABLE `design` (
  `id` bigint(20) NOT NULL auto_increment,
  `name` tinytext NOT NULL,
  `desc` text NOT NULL,
  `requirements` tinyblob,
  `time` bigint(20) NOT NULL default '0',
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `design`
--


--
-- Table structure for table `design_category`
--

DROP TABLE IF EXISTS `design_category`;
CREATE TABLE `design_category` (
  `design` bigint(20) NOT NULL default '0',
  `category` bigint(20) NOT NULL default '0',
  PRIMARY KEY  (`design`,`category`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `design_category`
--


--
-- Table structure for table `design_object`
--

DROP TABLE IF EXISTS `design_object`;
CREATE TABLE `design_object` (
  `design` bigint(20) NOT NULL default '0',
  `object` bigint(20) NOT NULL default '0',
  PRIMARY KEY  (`design`,`object`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `design_object`
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
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `object`
--

INSERT INTO `object` VALUES (-1,'sobjects.Universe','The Universe',100000000000,0,0,0,0,0,0,-1,0),(1,'sobjects.Galaxy','The Milky Way',10000000000,0,0,-6000,0,0,1000,0,0);

--
-- Table structure for table `object_extra`
--

DROP TABLE IF EXISTS `object_extra`;
CREATE TABLE `object_extra` (
  `object` bigint(20) NOT NULL default '0',
  `name` varchar(255) NOT NULL default '',
  `key` varchar(255) NOT NULL default '',
  `value` blob,
  PRIMARY KEY  (`object`,`name`,`key`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `object_extra`
--

INSERT INTO `object_extra` VALUES (0,'turn','','0');

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
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `order`
--


--
-- Table structure for table `order_extra`
--

DROP TABLE IF EXISTS `order_extra`;
CREATE TABLE `order_extra` (
  `order` bigint(20) NOT NULL default '0',
  `name` varchar(255) NOT NULL default '',
  `key` varchar(255) NOT NULL default '',
  `value` blob,
  PRIMARY KEY  (`order`,`name`,`key`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `order_extra`
--


--
-- Table structure for table `property`
--

DROP TABLE IF EXISTS `property`;
CREATE TABLE `property` (
  `id` bigint(20) NOT NULL auto_increment,
  `name` tinytext NOT NULL,
  `desc` text NOT NULL,
  `rank` tinyint(8) NOT NULL default '127',
  `requirements` tinyblob NOT NULL,
  `time` bigint(20) NOT NULL default '0',
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `property`
--


--
-- Table structure for table `property_category`
--

DROP TABLE IF EXISTS `property_category`;
CREATE TABLE `property_category` (
  `property` bigint(20) NOT NULL default '0',
  `category` bigint(20) NOT NULL default '0',
  PRIMARY KEY  (`property`,`category`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `property_category`
--


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
-- Dumping data for table `resource`
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

INSERT INTO `user` VALUES (1,'admin@tp','adminpassword',0);

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

UPDATE object SET id = 0 WHERE name='The Universe';
