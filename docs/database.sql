CREATE DATABASE tp;
USE tp;
-- MySQL dump 10.9
--
-- Host: localhost    Database: tp
-- ------------------------------------------------------
-- Server version	4.1.14-Debian_4-log
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO,MYSQL40,ANSI' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table "board"
--

CREATE TABLE "board" (
  "id" bigint(20) NOT NULL default '0',
  "name" tinyblob NOT NULL,
  "desc" blob NOT NULL,
  "time" bigint(20) NOT NULL default '0',
  PRIMARY KEY  ("id")
);

--
-- Dumping data for table "board"
--


--
-- Table structure for table "category"
--

CREATE TABLE "category" (
  "id" bigint(20) NOT NULL,
  "name" tinytext NOT NULL,
  "desc" text,
  "time" bigint(20) NOT NULL default '0',
  PRIMARY KEY  ("id")
);

--
-- Dumping data for table "category"
--

INSERT INTO "category" VALUES (1,'Misc','Things which don\'t fit into any specific category.',0);
INSERT INTO "category" VALUES (2,'Physical','Physical properties of an object.',0);
INSERT INTO "category" VALUES (3,'Components','Parts which make up a ship.',0);
INSERT INTO "category" VALUES (4,'Hulls','The basic frame work of a ship.',0);
INSERT INTO "category" VALUES (5,'Electrical','Things which go beep and consume electrical power.',0);

--
-- Table structure for table "component"
--

CREATE TABLE "component" (
  "id" bigint(20) NOT NULL,
  "name" tinytext NOT NULL,
  "desc" text NOT NULL,
  "requirements" blob,
  "comment" text,
  "time" bigint(20) NOT NULL default '0',
  PRIMARY KEY  ("id")
);

--
-- Dumping data for table "component"
--

INSERT INTO "component" VALUES (1,'Generic Component A','A very generic component (incompatible with component C).','','',0);
INSERT INTO "component" VALUES (2,'Generic Component B','A very generic electrical component.','','',0);
INSERT INTO "component" VALUES (3,'Generic Component C','A very generic component which uses both electrical and generic slots.','','',0);
INSERT INTO "component" VALUES (4,'Generic Hull','A very generic hull component that can have a small number of components added to it.','(lambda (design) 
	(if (> (designtype.hulls design) 1) 
		(cons #f \"Only one hull can be added to a design\") 
		(cons #t \"\")))','These Hulls can only be used in singular amounts',0);

--
-- Table structure for table "component_category"
--

CREATE TABLE "component_category" (
  "component" bigint(20) NOT NULL default '0',
  "category" bigint(20) NOT NULL default '0',
  "comment" text,
  PRIMARY KEY  ("component","category")
);

--
-- Dumping data for table "component_category"
--

INSERT INTO "component_category" VALUES (1,1,'Component A is a Misc');
INSERT INTO "component_category" VALUES (1,3,'Component A is a Component');
INSERT INTO "component_category" VALUES (2,3,'Component B is a Component');
INSERT INTO "component_category" VALUES (2,5,'Component B is a Electrical');
INSERT INTO "component_category" VALUES (3,3,'Component C is a Component');
INSERT INTO "component_category" VALUES (3,5,'Component C is a Electrical');
INSERT INTO "component_category" VALUES (4,4,'Hull A is a Hull');

--
-- Table structure for table "component_property"
--

CREATE TABLE "component_property" (
  "component" bigint(20) NOT NULL default '0',
  "property" bigint(20) NOT NULL default '0',
  "value" blob NOT NULL,
  "comment" text,
  PRIMARY KEY  ("component","property")
);

--
-- Dumping data for table "component_property"
--

INSERT INTO "component_property" VALUES (1,1,'(lambda (design) -1)','Component A uses 1 generic slot');
INSERT INTO "component_property" VALUES (1,2,'(lambda (design) (* (pow 10 3) 12))','Component A weighs 12 ton');
INSERT INTO "component_property" VALUES (2,2,'(lambda (design) (* (pow 10 3) 2))','Component B weighs 2 ton');
INSERT INTO "component_property" VALUES (2,5,'(lambda (design) -2)','Component B uses 2 electrical slots');
INSERT INTO "component_property" VALUES (3,1,'(lambda (design) -1)','Component C uses 1 generic slot');
INSERT INTO "component_property" VALUES (3,2,'(lambda (design) (* (pow 10 3) 3.2))','Component B weighs 3.2 ton');
INSERT INTO "component_property" VALUES (3,5,'(lambda (design) -1)','Component C uses 1 electrical slot');
INSERT INTO "component_property" VALUES (4,1,'(lambda (design) 5)','Hull A provides 5 generic slots');
INSERT INTO "component_property" VALUES (4,2,'(lambda (design) (* (+ (designtype.slots design) (designtype.slots-elec design)) (* (pow 10 3) 5)))','Hull A weighs 5ton per slot used.');
INSERT INTO "component_property" VALUES (4,5,'(lambda (design) 3)','Hull A provides 3 electrical slots');
INSERT INTO "component_property" VALUES (4,6,'(lambda (design) 1)','Hull A provides 1 hull');

--
-- Table structure for table "design"
--

CREATE TABLE "design" (
  "id" bigint(20) NOT NULL,
  "name" tinytext NOT NULL,
  "desc" text NOT NULL,
  "owner" bigint(20) NOT NULL default '0',
  "time" bigint(20) NOT NULL default '0',
  PRIMARY KEY  ("id")
);

--
-- Dumping data for table "design"
--

INSERT INTO "design" VALUES (1,'Test','A design for testing',1,0);

--
-- Table structure for table "design_category"
--

CREATE TABLE "design_category" (
  "design" bigint(20) NOT NULL default '0',
  "category" bigint(20) NOT NULL default '0',
  PRIMARY KEY  ("design","category")
);

--
-- Dumping data for table "design_category"
--

INSERT INTO "design_category" VALUES (1,1);

--
-- Table structure for table "design_component"
--

CREATE TABLE "design_component" (
  "design" bigint(20) NOT NULL default '0',
  "component" bigint(20) NOT NULL default '0',
  "amount" bigint(20) NOT NULL default '0',
  PRIMARY KEY  ("design","component")
);

--
-- Dumping data for table "design_component"
--

INSERT INTO "design_component" VALUES (1,1,2);

--
-- Table structure for table "message"
--

CREATE TABLE "message" (
  "id" bigint(20) NOT NULL,
  "bid" bigint(20) NOT NULL default '0',
  "slot" bigint(20) NOT NULL default '0',
  "subject" tinyblob NOT NULL,
  "body" blob NOT NULL,
  PRIMARY KEY  ("id")
);

--
-- Dumping data for table "message"
--


--
-- Table structure for table "object"
--

CREATE TABLE "object" (
  "id" bigint(20) NOT NULL,
  "type" varchar(255) NOT NULL default '',
  "name" tinyblob NOT NULL,
  "size" bigint(20) NOT NULL default '0',
  "posx" bigint(20) NOT NULL default '0',
  "posy" bigint(20) NOT NULL default '0',
  "posz" bigint(20) NOT NULL default '0',
  "velx" bigint(20) NOT NULL default '0',
  "vely" bigint(20) NOT NULL default '0',
  "velz" bigint(20) NOT NULL default '0',
  "parent" bigint(20) NOT NULL default '-1',
  "time" bigint(20) NOT NULL default '0',
  PRIMARY KEY  ("id")
);

--
-- Dumping data for table "object"
--

INSERT INTO "object" VALUES (-1,'sobjects.Universe','The Universe',100000000000,0,0,0,0,0,0,-1,0);
INSERT INTO "object" VALUES (1,'sobjects.Galaxy','The Milky Way',10000000000,0,0,-6000,0,0,1000,0,0);
INSERT INTO "object" VALUES (2,'sobjects.System','System 0',1102049,8687575000,3567274000,0,0,0,0,1,1129766512);
INSERT INTO "object" VALUES (3,'sobjects.Planet','Planet 0',3839,8687647000,3567275000,0,0,0,0,2,1129766512);
INSERT INTO "object" VALUES (4,'sobjects.Planet','Planet 1',8542,8687620000,3567324000,0,0,0,0,2,1129766512);
INSERT INTO "object" VALUES (5,'sobjects.Planet','Planet 2',8352,8687605000,3567359000,0,0,0,0,2,1129766512);
INSERT INTO "object" VALUES (6,'sobjects.System','System 1',1840168,5455353000,-7455800000,0,0,0,0,1,1129766512);
INSERT INTO "object" VALUES (7,'sobjects.Planet','Planet 8',4130,5455431000,-7455741000,0,0,0,0,6,1129766512);
INSERT INTO "object" VALUES (8,'sobjects.Planet','Planet 9',5329,5455379000,-7455714000,0,0,0,0,6,1129766513);
INSERT INTO "object" VALUES (9,'sobjects.Planet','Planet 10',3736,5455436000,-7455758000,0,0,0,0,6,1129766513);
INSERT INTO "object" VALUES (10,'sobjects.Planet','Planet 11',8214,5455423000,-7455721000,0,0,0,0,6,1129766513);
INSERT INTO "object" VALUES (11,'sobjects.Planet','Planet 12',2655,5455429000,-7455750000,0,0,0,0,6,1129766513);
INSERT INTO "object" VALUES (12,'sobjects.Planet','Planet 13',1191,5455419000,-7455721000,0,0,0,0,6,1129766513);
INSERT INTO "object" VALUES (13,'sobjects.System','System 2',1803442,-4897082000,-6160222000,0,0,0,0,1,1129766513);
INSERT INTO "object" VALUES (14,'sobjects.Planet','Planet 16',2473,-4897076000,-6160205000,0,0,0,0,13,1129766513);
INSERT INTO "object" VALUES (15,'sobjects.Planet','Planet 17',5544,-4897034000,-6160161000,0,0,0,0,13,1129766513);
INSERT INTO "object" VALUES (16,'sobjects.System','System 3',1431840,-4213329000,8468435000,0,0,0,0,1,1129766513);
INSERT INTO "object" VALUES (17,'sobjects.Planet','Planet 24',7625,-4213307000,8468529000,0,0,0,0,16,1129766513);
INSERT INTO "object" VALUES (18,'sobjects.Planet','Planet 25',1759,-4213307000,8468494000,0,0,0,0,16,1129766513);
INSERT INTO "object" VALUES (19,'sobjects.Planet','Planet 26',5907,-4213301000,8468492000,0,0,0,0,16,1129766513);
INSERT INTO "object" VALUES (20,'sobjects.Planet','Planet 27',3471,-4213253000,8468478000,0,0,0,0,16,1129766513);
INSERT INTO "object" VALUES (21,'sobjects.Planet','Planet 28',3444,-4213327000,8468534000,0,0,0,0,16,1129766513);
INSERT INTO "object" VALUES (22,'sobjects.Planet','Planet 29',9551,-4213245000,8468486000,0,0,0,0,16,1129766513);
INSERT INTO "object" VALUES (23,'sobjects.System','System 4',917398,-8776580000,-2691055000,0,0,0,0,1,1129766514);
INSERT INTO "object" VALUES (24,'sobjects.Planet','Planet 32',3505,-8776483000,-2691036000,0,0,0,0,23,1129766514);
INSERT INTO "object" VALUES (25,'sobjects.System','System 5',963168,4582430000,-829670000,0,0,0,0,1,1129766514);
INSERT INTO "object" VALUES (26,'sobjects.Planet','Planet 40',3723,4582432000,-829625000,0,0,0,0,25,1129766514);
INSERT INTO "object" VALUES (27,'sobjects.Planet','Planet 41',7079,4582472000,-829585000,0,0,0,0,25,1129766514);
INSERT INTO "object" VALUES (28,'sobjects.Planet','Planet 42',2402,4582483000,-829614000,0,0,0,0,25,1129766514);

--
-- Table structure for table "object_extra"
--

CREATE TABLE "object_extra" (
  "object" bigint(20) NOT NULL default '0',
  "name" varchar(255) NOT NULL default '',
  "key" varchar(255) NOT NULL default '',
  "value" blob,
  PRIMARY KEY  ("object","name","key")
);

--
-- Dumping data for table "object_extra"
--

INSERT INTO "object_extra" VALUES (0,'turn','','0');
INSERT INTO "object_extra" VALUES (3,'owner','','-1');
INSERT INTO "object_extra" VALUES (4,'owner','','-1');
INSERT INTO "object_extra" VALUES (5,'owner','','-1');
INSERT INTO "object_extra" VALUES (7,'owner','','-1');
INSERT INTO "object_extra" VALUES (8,'owner','','-1');
INSERT INTO "object_extra" VALUES (9,'owner','','-1');
INSERT INTO "object_extra" VALUES (10,'owner','','-1');
INSERT INTO "object_extra" VALUES (11,'owner','','-1');
INSERT INTO "object_extra" VALUES (12,'owner','','-1');
INSERT INTO "object_extra" VALUES (14,'owner','','-1');
INSERT INTO "object_extra" VALUES (15,'owner','','-1');
INSERT INTO "object_extra" VALUES (17,'owner','','-1');
INSERT INTO "object_extra" VALUES (18,'owner','','-1');
INSERT INTO "object_extra" VALUES (19,'owner','','-1');
INSERT INTO "object_extra" VALUES (20,'owner','','-1');
INSERT INTO "object_extra" VALUES (21,'owner','','-1');
INSERT INTO "object_extra" VALUES (22,'owner','','-1');
INSERT INTO "object_extra" VALUES (24,'owner','','-1');
INSERT INTO "object_extra" VALUES (26,'owner','','-1');
INSERT INTO "object_extra" VALUES (27,'owner','','-1');
INSERT INTO "object_extra" VALUES (28,'owner','','-1');

--
-- Table structure for table "order"
--

CREATE TABLE "order" (
  "id" bigint(20) NOT NULL,
  "type" varchar(255) NOT NULL default '',
  "oid" bigint(20) NOT NULL default '0',
  "slot" bigint(20) NOT NULL default '0',
  "worked" bigint(20) NOT NULL default '0',
  PRIMARY KEY  ("id")
);

--
-- Dumping data for table "order"
--


--
-- Table structure for table "order_extra"
--

CREATE TABLE "order_extra" (
  "order" bigint(20) NOT NULL default '0',
  "name" varchar(255) NOT NULL default '',
  "key" varchar(255) NOT NULL default '',
  "value" blob,
  PRIMARY KEY  ("order","name","key")
);

--
-- Dumping data for table "order_extra"
--


--
-- Table structure for table "property"
--

CREATE TABLE "property" (
  "id" bigint(20) NOT NULL,
  "name" tinytext NOT NULL,
  "display_name" tinytext NOT NULL,
  "desc" text NOT NULL,
  "rank" tinyint(8) NOT NULL default '127',
  "calculate" blob NOT NULL,
  "requirements" blob NOT NULL,
  "comment" text,
  "time" bigint(20) NOT NULL default '0',
  PRIMARY KEY  ("id")
);

--
-- Dumping data for table "property"
--

INSERT INTO "property" VALUES (1,'slots','Generic Slots','Number of generic slots',1,'(lambda (design bits) 
	(let ((n (apply + bits))) 
		(cons n 
			(string-append (number->string n) \" Slots\"))))','(lambda (design) 
	(if (> (designtype.slots design) 0) 
		(cons #t \"\") 
		(cons #f \"Too many generic slots are used\")))','Generic slots must not go negative. Is formated like \"12 Slots\"',0);
INSERT INTO "property" VALUES (2,'mass','Mass','How massive (heavy) something is.',10,'(lambda (design bits) 
	(let ((n (apply + bits))) 
		(cond 
			((> n (pow 10 7)) (cons n (string-append (number->string (/ n (pow 10 6))) \" kt\")) ) 
			((> n (pow 10 4)) (cons n (string-append (number->string (/ n (pow 10 3))) \" t\")) ) 
			(#t (cons n (string-append (number->string n) \" kg\")) ) 
		)))','(lambda (design) 
	(if (< (designtype.mass design) 0) 
		(cons #f \"Mass is negative! This is a bug, please report this bug to ...\") 
		(cons #t \"\")))','This should show masses under 10 ton in \"<> kg\", masses under 10 kt in \"<> t\" and the rest in \"<> kt\". Mass should never be negative.',0);
INSERT INTO "property" VALUES (3,'thrust','Thrust','How much lateral force the device has',10,'(lambda (design bits) 
	(let ((n (apply + bits))) 
		(cons n (string-append (number->string n) \" N\"))))','(lambda (design) 
	(if (< (designtype.thrust design) 0) 
		(cons #f \"Thrust is negative! This is a bug, please report this bug to ...\") 
		(cons #t \"\")))','This should display a \" N\" (which is short for newtons). Thrust should never be negative.',0);
INSERT INTO "property" VALUES (4,'acceleration','Acceleration','How quickly the device accelerates',20,'(lambda (design bits) 
	(let ((n (/ (designtype.thrust design) (designtype.mass design)))) 
		(cons n (string-append n \" m/s^2\"))))','(lambda (design) 
	(if (< (designtype.acceleration design) 0) 
		(cons #f \"Acceleration is negative! This is a bug, please report this bug to ...\") 
		(if (< (designtype.acceleration design) 1000) 
			(if (!= (designtype.thrust design) 0) 
				(cons #t \"The design is so slow it is basically unmovable.\") 
				(cons #t \"\")) 
			(cons #t \"\"))))','Acceleration is displayed in m/s^2, a warning is issued if the acceleration is practically non-existant.',0);
INSERT INTO "property" VALUES (5,'slots-elec','Electrical Slots','Number of electrical slot',1,'(lambda (design bits) 
	(let ((n (apply + bits))) 
		(cons n (string-append (number->string n) \" Slots\"))))','(lambda (design) 
	(if (< (designtype.slots-elec design) 0) 
		(cons #f \"Too many electrical slots are used\") 
		(cons #t \"\")))','Electrical slots must not go negative. Is formated like \"12 Slots\"',0);
INSERT INTO "property" VALUES (6,'hulls','Hulls','Number of hulls in a design',10,'(lambda (design bits) 
	(let ((n (apply + bits))) 
		(cons n \"\")))','(lambda (design) (cons #t \"\"))','A hidden property which just counts the number of hulls in a design',0);

--
-- Table structure for table "property_category"
--

CREATE TABLE "property_category" (
  "property" bigint(20) NOT NULL default '0',
  "category" bigint(20) NOT NULL default '0',
  PRIMARY KEY  ("property","category")
);

--
-- Dumping data for table "property_category"
--

INSERT INTO "property_category" VALUES (1,1);
INSERT INTO "property_category" VALUES (2,2);
INSERT INTO "property_category" VALUES (3,2);
INSERT INTO "property_category" VALUES (4,2);
INSERT INTO "property_category" VALUES (5,1);

--
-- Table structure for table "resource"
--

CREATE TABLE "resource" (
  "id" bigint(20) NOT NULL,
  "namesingular" tinytext NOT NULL,
  "nameplural" tinytext NOT NULL,
  "unitsingular" tinytext NOT NULL,
  "unitplural" tinytext NOT NULL,
  "desc" text,
  "weight" bigint(20) NOT NULL default '0',
  "size" bigint(20) NOT NULL default '0',
  "time" bigint(20) NOT NULL default '0',
  PRIMARY KEY  ("id")
);

--
-- Dumping data for table "resource"
--


--
-- Table structure for table "user"
--

CREATE TABLE "user" (
  "id" bigint(20) NOT NULL,
  "username" tinyblob NOT NULL,
  "password" tinyblob NOT NULL,
  "time" bigint(20) NOT NULL default '0',
  PRIMARY KEY  ("id")
);

--
-- Dumping data for table "user"
--

INSERT INTO "user" VALUES (1,'admin@tp','adminpassword',0);

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

UPDATE object SET id = 0 WHERE name='The Universe';
