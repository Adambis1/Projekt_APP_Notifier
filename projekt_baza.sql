-- phpMyAdmin SQL Dump
-- version 5.1.3
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Czas generowania: 11 Kwi 2022, 11:44
-- Wersja serwera: 10.4.24-MariaDB
-- Wersja PHP: 7.4.28

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Baza danych: `app`
--
CREATE DATABASE IF NOT EXISTS `app` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `app`;

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `parowanie`
--

DROP TABLE IF EXISTS `parowanie`;
CREATE TABLE IF NOT EXISTS `parowanie` (
  `recipient_id` int(11) NOT NULL,
  `date` datetime NOT NULL,
  `kod` int(11) NOT NULL,
  KEY `recipient_id` (`recipient_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `todo`
--

DROP TABLE IF EXISTS `todo`;
CREATE TABLE IF NOT EXISTS `todo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `recipient_id` int(11) NOT NULL,
  `Text` text NOT NULL,
  `data` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `recipient_id` (`recipient_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `users`
--

DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
  `recipient_id` int(11) NOT NULL AUTO_INCREMENT,
  `facebook_id` bigint(20) DEFAULT NULL,
  `telegram_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`recipient_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Ograniczenia dla zrzutów tabel
--

--
-- Ograniczenia dla tabeli `parowanie`
--
ALTER TABLE `parowanie`
  ADD CONSTRAINT `parowanie_ibfk_1` FOREIGN KEY (`recipient_id`) REFERENCES `users` (`recipient_id`);

--
-- Ograniczenia dla tabeli `todo`
--
ALTER TABLE `todo`
  ADD CONSTRAINT `ToDo_ibfk_1` FOREIGN KEY (`recipient_id`) REFERENCES `users` (`recipient_id`);
COMMIT;

SET GLOBAL TRANSACTION ISOLATION LEVEL READ COMMITTED;

GRANT USAGE ON *.* TO `app`@`%` IDENTIFIED BY PASSWORD '*0ED1B7A19B0F944DCE05490E42370695B412986E';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE TEMPORARY TABLES, EXECUTE, SHOW VIEW ON `app`.* TO `app`@`%`;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
