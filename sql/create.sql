-- Adminer 4.3.1 MySQL dump

SET NAMES utf8;
SET time_zone = '+00:00';

CREATE DATABASE `poderopedia` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `poderopedia`;

DROP TABLE IF EXISTS `connection`;
CREATE TABLE `connection` (
  `idconnection` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(15) NOT NULL,
  `source_path` varchar(125) DEFAULT NULL,
  `target_path` varchar(125) DEFAULT NULL,
  `relationship` varchar(180) DEFAULT NULL,
  `when` varchar(60) DEFAULT NULL,
  `where` varchar(185) DEFAULT NULL,
  `source` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`idconnection`),
  KEY `idx_path` (`target_path`),
  KEY `idx_type` (`type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

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
  `mainsector` varchar(50) DEFAULT NULL,
  `date_of_birth` datetime DEFAULT NULL,
  `abstract` text,
  `profile` longtext,
  `last_update` datetime DEFAULT NULL,
  PRIMARY KEY (`idperson`),
  UNIQUE KEY `path_UNIQUE` (`path`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- 2017-10-12 19:27:49
