-- MySQL dump 9.11
--
-- Host: localhost    Database: tp
-- ------------------------------------------------------
-- Server version	4.0.20-log

--
-- Table structure for table `object`
--

DROP TABLE IF EXISTS object;
CREATE TABLE object (
  id bigint(20) NOT NULL auto_increment,
  type bigint(20) NOT NULL default '0',
  name tinyblob NOT NULL,
  size bigint(20) NOT NULL default '0',
  posx bigint(20) NOT NULL default '0',
  posy bigint(20) NOT NULL default '0',
  posz bigint(20) NOT NULL default '0',
  velx bigint(20) NOT NULL default '0',
  vely bigint(20) NOT NULL default '0',
  velz bigint(20) NOT NULL default '0',
  parent bigint(20) NOT NULL default '-1',
  PRIMARY KEY  (id)
) TYPE=MyISAM;

--
-- Dumping data for table `object`
--

INSERT INTO object VALUES (0,0,'The Universe',100000000000,0,0,0,0,0,0,-1);

--
-- Table structure for table `object_attr`
--

DROP TABLE IF EXISTS object_attr;
CREATE TABLE object_attr (
  object_id bigint(20) NOT NULL default '0',
  object_type_attr_id bigint(20) NOT NULL default '0',
  value blob NOT NULL,
  PRIMARY KEY  (object_id,object_type_attr_id)
) TYPE=MyISAM;

--
-- Dumping data for table `object_attr`
--

INSERT INTO object_attr VALUES (0,1,'I0\n.');

--
-- Table structure for table `object_order_type`
--

DROP TABLE IF EXISTS object_order_type;
CREATE TABLE object_order_type (
  object_id bigint(20) NOT NULL default '0',
  order_type_id bigint(20) NOT NULL default '0',
  PRIMARY KEY  (object_id,order_type_id)
) TYPE=MyISAM;

--
-- Dumping data for table `object_order_type`
--


--
-- Table structure for table `object_type`
--

DROP TABLE IF EXISTS object_type;
CREATE TABLE object_type (
  id bigint(20) NOT NULL auto_increment,
  name tinyblob NOT NULL,
  PRIMARY KEY  (id)
) TYPE=MyISAM;

--
-- Dumping data for table `object_type`
--

INSERT INTO object_type VALUES (0,'Universe');
INSERT INTO object_type VALUES (1,'Galaxy');
INSERT INTO object_type VALUES (2,'Star System');
INSERT INTO object_type VALUES (3,'Planet');
INSERT INTO object_type VALUES (4,'Fleet');

--
-- Table structure for table `object_type_attr`
--

DROP TABLE IF EXISTS object_type_attr;
CREATE TABLE object_type_attr (
  id bigint(20) NOT NULL auto_increment,
  object_type_id bigint(20) NOT NULL default '0',
  name tinyblob NOT NULL,
  PRIMARY KEY  (id)
) TYPE=MyISAM;

--
-- Dumping data for table `object_type_attr`
--

INSERT INTO object_type_attr VALUES (1,0,'turn');
INSERT INTO object_type_attr VALUES (2,3,'owner');
INSERT INTO object_type_attr VALUES (3,4,'owner');

--
-- Table structure for table `order`
--

DROP TABLE IF EXISTS order;
CREATE TABLE order (
  id bigint(20) NOT NULL auto_increment,
  oid bigint(20) NOT NULL default '0',
  slot bigint(20) NOT NULL default '0',
  type bigint(20) NOT NULL default '0',
  PRIMARY KEY  (id)
) TYPE=MyISAM;

--
-- Dumping data for table `order`
--

INSERT INTO order VALUES (20,0,1,0);
INSERT INTO order VALUES (21,0,2,0);
INSERT INTO order VALUES (22,0,0,0);

--
-- Table structure for table `order_attr`
--

DROP TABLE IF EXISTS order_attr;
CREATE TABLE order_attr (
  order_id bigint(20) NOT NULL default '0',
  order_type_attr_id bigint(20) NOT NULL default '0',
  value blob,
  PRIMARY KEY  (order_id,order_type_attr_id)
) TYPE=MyISAM;

--
-- Dumping data for table `order_attr`
--

INSERT INTO order_attr VALUES (20,1,'L2L\n.');
INSERT INTO order_attr VALUES (21,1,'L1L\n.');
INSERT INTO order_attr VALUES (22,1,'L22L\n.');

--
-- Table structure for table `order_type`
--

DROP TABLE IF EXISTS order_type;
CREATE TABLE order_type (
  id bigint(20) NOT NULL auto_increment,
  name tinyblob NOT NULL,
  PRIMARY KEY  (id)
) TYPE=MyISAM;

--
-- Dumping data for table `order_type`
--

INSERT INTO order_type VALUES (0,'NOp');
INSERT INTO order_type VALUES (1,'Move');

--
-- Table structure for table `order_type_attr`
--

DROP TABLE IF EXISTS order_type_attr;
CREATE TABLE order_type_attr (
  id bigint(20) NOT NULL auto_increment,
  order_type_id bigint(20) NOT NULL default '0',
  name tinyblob NOT NULL,
  type tinyint(4) NOT NULL default '0',
  description blob,
  PRIMARY KEY  (id)
) TYPE=MyISAM;

--
-- Dumping data for table `order_type_attr`
--

INSERT INTO order_type_attr VALUES (1,0,'wait',0,'Wait this long.');
INSERT INTO order_type_attr VALUES (2,1,'pos',0,'Move to position.');

--
-- Table structure for table `resource`
--

DROP TABLE IF EXISTS resource;
CREATE TABLE resource (
  id bigint(20) NOT NULL auto_increment,
  name_singular tinyblob NOT NULL,
  name_plural tinyblob NOT NULL,
  unit_singular tinyblob NOT NULL,
  unit_plural tinyblob NOT NULL,
  description blob NOT NULL,
  weight bigint(20) NOT NULL default '0',
  size bigint(20) NOT NULL default '0',
  PRIMARY KEY  (id)
) TYPE=MyISAM;

--
-- Dumping data for table `resource`
--


--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS user;
CREATE TABLE user (
  id bigint(20) NOT NULL auto_increment,
  username tinyblob NOT NULL,
  password tinyblob NOT NULL,
  PRIMARY KEY  (id)
) TYPE=MyISAM;

--
-- Dumping data for table `user`
--

INSERT INTO user VALUES (1,'mithro','password');
INSERT INTO user VALUES (2,'lee','lee-password');

