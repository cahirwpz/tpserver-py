-- MySQL dump 9.11
--
-- Host: mithro.dyndns.org    Database: tp
-- ------------------------------------------------------
-- Server version	4.0.13-log

--
-- Table structure for table `board`
--

DROP TABLE IF EXISTS board;
CREATE TABLE board (
  id bigint(20) NOT NULL default '0',
  name tinyblob NOT NULL,
  desc blob NOT NULL,
  PRIMARY KEY  (id)
) TYPE=MyISAM;

--
-- Dumping data for table `board`
--

INSERT INTO board VALUES (11,'Private message board for t','This board is used so that stuff you own (such as fleets and planets) can inform you of what is happening in the universe. ');

--
-- Table structure for table `message`
--

DROP TABLE IF EXISTS message;
CREATE TABLE message (
  id bigint(20) NOT NULL auto_increment,
  bid bigint(20) NOT NULL default '0',
  slot bigint(20) NOT NULL default '0',
  subject tinyblob NOT NULL,
  body blob NOT NULL,
  PRIMARY KEY  (id)
) TYPE=MyISAM;

--
-- Dumping data for table `message`
--

INSERT INTO message VALUES (1,11,0,'First Fleet arrived','First Fleet has arrive at it\'s destination.');

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
INSERT INTO object VALUES (25,1,'The Milky Way',10000000000,0,0,-6000,0,0,1000,0);
INSERT INTO object VALUES (26,2,'The Sol Terra System',1400000,3000000000,2000000000,0,-1500000,1500000,0,25);
INSERT INTO object VALUES (27,2,'The Alpha Centauri System',800000,-1500000000,1500000000,0,-1000000,-1000000,0,25);
INSERT INTO object VALUES (28,2,'Sirius System',2000000,-250000000,-4000000000,0,2300000,0,0,25);
INSERT INTO object VALUES (55,4,'First Fleet',1,2147483647,-2147483647,-2147483647,0,0,0,0);
INSERT INTO object VALUES (54,3,'Unknown planet',7207,67203857,-9289417568,-7649254180,0,0,0,52);
INSERT INTO object VALUES (53,3,'t\'s Homeworld',1000,67203857,-9289417568,-7649254180,0,0,0,52);
INSERT INTO object VALUES (52,2,'t\'s System',1630922,67203857,-9289417568,-7649254180,0,0,0,0);

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
INSERT INTO object_attr VALUES (55,3,'L11L\n.');
INSERT INTO object_attr VALUES (54,2,'I0\n.');
INSERT INTO object_attr VALUES (53,2,'L11L\n.');

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
  default blob NOT NULL,
  PRIMARY KEY  (id)
) TYPE=MyISAM;

--
-- Dumping data for table `object_type_attr`
--

INSERT INTO object_type_attr VALUES (1,0,'turn','I0\n.');
INSERT INTO object_type_attr VALUES (2,3,'owner','I-1\n.');
INSERT INTO object_type_attr VALUES (3,4,'owner','I-1\n.');

--
-- Table structure for table `object_type_order_type`
--

DROP TABLE IF EXISTS object_type_order_type;
CREATE TABLE object_type_order_type (
  object_type_id bigint(20) NOT NULL default '0',
  order_type_id bigint(20) NOT NULL default '0',
  PRIMARY KEY  (object_type_id,order_type_id)
) TYPE=MyISAM;

--
-- Dumping data for table `object_type_order_type`
--

INSERT INTO object_type_order_type VALUES (3,0);
INSERT INTO object_type_order_type VALUES (3,2);
INSERT INTO object_type_order_type VALUES (4,0);
INSERT INTO object_type_order_type VALUES (4,1);

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

INSERT INTO order VALUES (70,55,3,0);
INSERT INTO order VALUES (75,55,2,1);
INSERT INTO order VALUES (76,55,1,0);
INSERT INTO order VALUES (78,55,0,0);

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

INSERT INTO order_attr VALUES (75,2,'(L0L\nL1000L\nL10L\ntp1\n.');
INSERT INTO order_attr VALUES (76,1,'L22\n.');
INSERT INTO order_attr VALUES (78,1,'L22L\n.');
INSERT INTO order_attr VALUES (70,1,'I0\n.');

--
-- Table structure for table `order_type`
--

DROP TABLE IF EXISTS order_type;
CREATE TABLE order_type (
  id bigint(20) NOT NULL auto_increment,
  name tinyblob NOT NULL,
  desc blob,
  PRIMARY KEY  (id)
) TYPE=MyISAM;

--
-- Dumping data for table `order_type`
--

INSERT INTO order_type VALUES (0,'NOp','Do nothing for a period.');
INSERT INTO order_type VALUES (1,'Move','Move to a location.');
INSERT INTO order_type VALUES (2,'Build Fleet','Build some new ships!');

--
-- Table structure for table `order_type_attr`
--

DROP TABLE IF EXISTS order_type_attr;
CREATE TABLE order_type_attr (
  id bigint(20) NOT NULL auto_increment,
  order_type_id bigint(20) NOT NULL default '0',
  name tinyblob NOT NULL,
  type tinyint(4) NOT NULL default '0',
  desc blob,
  default blob NOT NULL,
  PRIMARY KEY  (id)
) TYPE=MyISAM;

--
-- Dumping data for table `order_type_attr`
--

INSERT INTO order_type_attr VALUES (1,0,'wait',1,'Wait this long.','I0\n.');
INSERT INTO order_type_attr VALUES (2,1,'pos',0,'Move to position.','(I0\nI0\nI0\ntp0\n.');
INSERT INTO order_type_attr VALUES (3,2,'ships',4,'Number of ships to build in this fleet.','I0\n.');

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

INSERT INTO user VALUES (11,'t','t');

