-- Adminer 4.3.1 MySQL dump

SET NAMES utf8;
SET time_zone = '+00:00';

DROP DATABASE IF EXISTS `poderopedia`;
CREATE DATABASE `poderopedia` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `poderopedia`;

DROP TABLE IF EXISTS `company`;
CREATE TABLE `company` (
  `idcompany` int(11) NOT NULL AUTO_INCREMENT,
  `path` varchar(125) DEFAULT NULL,
  `alias` varchar(120) DEFAULT NULL,
  `has_social_reason` varchar(120) DEFAULT NULL,
  `birth` varchar(25) DEFAULT NULL,
  `countryof_residence` varchar(25) DEFAULT NULL,
  `mainsector` varchar(125) DEFAULT NULL,
  `date_of_birth` datetime DEFAULT NULL,
  `abstract` text,
  `profile` longtext,
  `last_update` datetime DEFAULT NULL,
  PRIMARY KEY (`idcompany`),
  UNIQUE KEY `path_UNIQUE` (`path`)
) ENGINE=InnoDB AUTO_INCREMENT=1701 DEFAULT CHARSET=utf8;


DROP VIEW IF EXISTS `company_company`;
CREATE TABLE `company_company` (`idconnection` int(11), `source_path` varchar(125), `target_path` varchar(125), `relationship` varchar(250), `when` varchar(60), `where` varchar(185), `source` varchar(1000));


DROP VIEW IF EXISTS `company_member`;
CREATE TABLE `company_member` (`idconnection` int(11), `source_path` varchar(125), `target_path` varchar(125), `relationship` varchar(250), `when` varchar(60), `where` varchar(185), `source` varchar(1000));


DROP VIEW IF EXISTS `company_organization`;
CREATE TABLE `company_organization` (`idconnection` int(11), `source_path` varchar(125), `target_path` varchar(125), `relationship` varchar(250), `when` varchar(60), `where` varchar(185), `source` varchar(1000));


DROP TABLE IF EXISTS `connection`;
CREATE TABLE `connection` (
  `idconnection` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(15) NOT NULL,
  `source_path` varchar(125) DEFAULT NULL,
  `target_path` varchar(125) DEFAULT NULL,
  `relationship` varchar(250) DEFAULT NULL,
  `when` varchar(60) DEFAULT NULL,
  `where` varchar(185) DEFAULT NULL,
  `source` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`idconnection`),
  KEY `idx_path` (`target_path`),
  KEY `idx_type` (`type`)
) ENGINE=InnoDB AUTO_INCREMENT=25331 DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `organization`;
CREATE TABLE `organization` (
  `idorganization` int(11) NOT NULL AUTO_INCREMENT,
  `path` varchar(125) DEFAULT NULL,
  `alias` varchar(120) DEFAULT NULL,
  `has_social_reason` varchar(120) DEFAULT NULL,
  `birth` varchar(25) DEFAULT NULL,
  `countryof_residence` varchar(25) DEFAULT NULL,
  `mainsector` varchar(125) DEFAULT NULL,
  `date_of_birth` datetime DEFAULT NULL,
  `abstract` text,
  `profile` longtext,
  `last_update` datetime DEFAULT NULL,
  PRIMARY KEY (`idorganization`),
  UNIQUE KEY `path_UNIQUE` (`path`)
) ENGINE=InnoDB AUTO_INCREMENT=1045 DEFAULT CHARSET=utf8;


DROP VIEW IF EXISTS `organization_company`;
CREATE TABLE `organization_company` (`idconnection` int(11), `source_path` varchar(125), `target_path` varchar(125), `relationship` varchar(250), `when` varchar(60), `where` varchar(185), `source` varchar(1000));


DROP VIEW IF EXISTS `organization_member`;
CREATE TABLE `organization_member` (`idconnection` int(11), `source_path` varchar(125), `target_path` varchar(125), `relationship` varchar(250), `when` varchar(60), `where` varchar(185), `source` varchar(1000));


DROP VIEW IF EXISTS `organization_organization`;
CREATE TABLE `organization_organization` (`idconnection` int(11), `source_path` varchar(125), `target_path` varchar(125), `relationship` varchar(250), `when` varchar(60), `where` varchar(185), `source` varchar(1000));


DROP TABLE IF EXISTS `person`;
CREATE TABLE `person` (
  `idperson` int(11) NOT NULL AUTO_INCREMENT,
  `path` varchar(125) DEFAULT NULL,
  `alias` varchar(120) DEFAULT NULL,
  `first_name` varchar(40) DEFAULT NULL,
  `first_last_name` varchar(40) DEFAULT NULL,
  `other_last_name` varchar(40) DEFAULT NULL,
  `birth` varchar(25) DEFAULT NULL,
  `countryof_residence` varchar(25) DEFAULT NULL,
  `mainsector` varchar(125) DEFAULT NULL,
  `date_of_birth` datetime DEFAULT NULL,
  `abstract` text,
  `profile` longtext,
  `last_update` datetime DEFAULT NULL,
  PRIMARY KEY (`idperson`),
  UNIQUE KEY `path_UNIQUE` (`path`)
) ENGINE=InnoDB AUTO_INCREMENT=1760 DEFAULT CHARSET=utf8;


DROP VIEW IF EXISTS `person_advisor`;
CREATE TABLE `person_advisor` (`idconnection` int(11), `source_path` varchar(125), `target_path` varchar(125), `relationship` varchar(250), `when` varchar(60), `where` varchar(185), `source` varchar(1000));


DROP VIEW IF EXISTS `person_classmate`;
CREATE TABLE `person_classmate` (`idconnection` int(11), `source_path` varchar(125), `target_path` varchar(125), `relationship` varchar(250), `when` varchar(60), `where` varchar(185), `source` varchar(1000));


DROP VIEW IF EXISTS `person_company`;
CREATE TABLE `person_company` (`idconnection` int(11), `source_path` varchar(125), `target_path` varchar(125), `relationship` varchar(250), `when` varchar(60), `where` varchar(185), `source` varchar(1000));


DROP VIEW IF EXISTS `person_couple`;
CREATE TABLE `person_couple` (`idconnection` int(11), `source_path` varchar(125), `target_path` varchar(125), `relationship` varchar(250), `when` varchar(60), `where` varchar(185), `source` varchar(1000));


DROP VIEW IF EXISTS `person_family`;
CREATE TABLE `person_family` (`idconnection` int(11), `source_path` varchar(125), `target_path` varchar(125), `relationship` varchar(250), `when` varchar(60), `where` varchar(185), `source` varchar(1000));


DROP VIEW IF EXISTS `person_friend`;
CREATE TABLE `person_friend` (`idconnection` int(11), `source_path` varchar(125), `target_path` varchar(125), `relationship` varchar(250), `when` varchar(60), `where` varchar(185), `source` varchar(1000));


DROP VIEW IF EXISTS `person_organization`;
CREATE TABLE `person_organization` (`idconnection` int(11), `source_path` varchar(125), `target_path` varchar(125), `relationship` varchar(250), `when` varchar(60), `where` varchar(185), `source` varchar(1000));


DROP TABLE IF EXISTS `company_company`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `company_company` AS select `connection`.`idconnection` AS `idconnection`,`connection`.`source_path` AS `source_path`,`connection`.`target_path` AS `target_path`,`connection`.`relationship` AS `relationship`,`connection`.`when` AS `when`,`connection`.`where` AS `where`,`connection`.`source` AS `source` from `connection` where ((`connection`.`type` = 'organization') and (`connection`.`source_path` like '/cl/empresas/%') and (`connection`.`target_path` like '/cl/empresas/%'));

DROP TABLE IF EXISTS `company_member`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `company_member` AS select `connection`.`idconnection` AS `idconnection`,`connection`.`source_path` AS `source_path`,`connection`.`target_path` AS `target_path`,`connection`.`relationship` AS `relationship`,`connection`.`when` AS `when`,`connection`.`where` AS `where`,`connection`.`source` AS `source` from `connection` where ((`connection`.`type` = 'member') and (`connection`.`source_path` like '/cl/empresas/%'));

DROP TABLE IF EXISTS `company_organization`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `company_organization` AS select `connection`.`idconnection` AS `idconnection`,`connection`.`source_path` AS `source_path`,`connection`.`target_path` AS `target_path`,`connection`.`relationship` AS `relationship`,`connection`.`when` AS `when`,`connection`.`where` AS `where`,`connection`.`source` AS `source` from `connection` where ((`connection`.`type` = 'organization') and (`connection`.`source_path` like '/cl/empresas/%') and (`connection`.`target_path` like '/cl/organizaciones/%'));

DROP TABLE IF EXISTS `organization_company`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `organization_company` AS select `connection`.`idconnection` AS `idconnection`,`connection`.`source_path` AS `source_path`,`connection`.`target_path` AS `target_path`,`connection`.`relationship` AS `relationship`,`connection`.`when` AS `when`,`connection`.`where` AS `where`,`connection`.`source` AS `source` from `connection` where ((`connection`.`type` = 'organization') and (`connection`.`source_path` like '/cl/organizaciones/%') and (`connection`.`target_path` like '/cl/empresas/%'));

DROP TABLE IF EXISTS `organization_member`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `organization_member` AS select `connection`.`idconnection` AS `idconnection`,`connection`.`source_path` AS `source_path`,`connection`.`target_path` AS `target_path`,`connection`.`relationship` AS `relationship`,`connection`.`when` AS `when`,`connection`.`where` AS `where`,`connection`.`source` AS `source` from `connection` where ((`connection`.`type` = 'member') and (`connection`.`source_path` like '/cl/organizaciones/%') and (`connection`.`target_path` like '/cl/personas/%'));

DROP TABLE IF EXISTS `organization_organization`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `organization_organization` AS select `connection`.`idconnection` AS `idconnection`,`connection`.`source_path` AS `source_path`,`connection`.`target_path` AS `target_path`,`connection`.`relationship` AS `relationship`,`connection`.`when` AS `when`,`connection`.`where` AS `where`,`connection`.`source` AS `source` from `connection` where ((`connection`.`type` = 'organization') and (`connection`.`source_path` like '/cl/organizaciones/%') and (`connection`.`target_path` like '/cl/organizaciones/%'));

DROP TABLE IF EXISTS `person_advisor`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `person_advisor` AS select `connection`.`idconnection` AS `idconnection`,`connection`.`source_path` AS `source_path`,`connection`.`target_path` AS `target_path`,`connection`.`relationship` AS `relationship`,`connection`.`when` AS `when`,`connection`.`where` AS `where`,`connection`.`source` AS `source` from `connection` where ((`connection`.`type` = 'advisor') and (`connection`.`source_path` like '/cl/personas/%'));

DROP TABLE IF EXISTS `person_classmate`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `person_classmate` AS select `connection`.`idconnection` AS `idconnection`,`connection`.`source_path` AS `source_path`,`connection`.`target_path` AS `target_path`,`connection`.`relationship` AS `relationship`,`connection`.`when` AS `when`,`connection`.`where` AS `where`,`connection`.`source` AS `source` from `connection` where ((`connection`.`type` = 'classmate') and (`connection`.`source_path` like '/cl/personas/%'));

DROP TABLE IF EXISTS `person_company`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `person_company` AS select `connection`.`idconnection` AS `idconnection`,`connection`.`source_path` AS `source_path`,`connection`.`target_path` AS `target_path`,`connection`.`relationship` AS `relationship`,`connection`.`when` AS `when`,`connection`.`where` AS `where`,`connection`.`source` AS `source` from `connection` where ((`connection`.`type` = 'organization') and (`connection`.`source_path` like '/cl/personas/%') and (`connection`.`target_path` like '/cl/empresas/%'));

DROP TABLE IF EXISTS `person_couple`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `person_couple` AS select `connection`.`idconnection` AS `idconnection`,`connection`.`source_path` AS `source_path`,`connection`.`target_path` AS `target_path`,`connection`.`relationship` AS `relationship`,`connection`.`when` AS `when`,`connection`.`where` AS `where`,`connection`.`source` AS `source` from `connection` where ((`connection`.`type` = 'couple') and (`connection`.`source_path` like '/cl/personas/%'));

DROP TABLE IF EXISTS `person_family`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `person_family` AS select `connection`.`idconnection` AS `idconnection`,`connection`.`source_path` AS `source_path`,`connection`.`target_path` AS `target_path`,`connection`.`relationship` AS `relationship`,`connection`.`when` AS `when`,`connection`.`where` AS `where`,`connection`.`source` AS `source` from `connection` where (`connection`.`type` = 'family');

DROP TABLE IF EXISTS `person_friend`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `person_friend` AS select `connection`.`idconnection` AS `idconnection`,`connection`.`source_path` AS `source_path`,`connection`.`target_path` AS `target_path`,`connection`.`relationship` AS `relationship`,`connection`.`when` AS `when`,`connection`.`where` AS `where`,`connection`.`source` AS `source` from `connection` where (`connection`.`type` = 'friend');

DROP TABLE IF EXISTS `person_organization`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `person_organization` AS select `connection`.`idconnection` AS `idconnection`,`connection`.`source_path` AS `source_path`,`connection`.`target_path` AS `target_path`,`connection`.`relationship` AS `relationship`,`connection`.`when` AS `when`,`connection`.`where` AS `where`,`connection`.`source` AS `source` from `connection` where ((`connection`.`type` = 'organization') and (`connection`.`source_path` like '/cl/personas/%') and (`connection`.`target_path` like '/cl/organizaciones/%'));

-- 2017-10-20 01:25:33

