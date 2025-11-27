-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 26, 2025 at 05:34 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `news_portal`
--

-- --------------------------------------------------------

--
-- Table structure for table `articles`
--

CREATE TABLE `articles` (
  `article_id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `content` text NOT NULL,
  `author_id` int(11) DEFAULT NULL,
  `category_id` int(11) DEFAULT NULL,
  `publication_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `is_published` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `articles`
--

INSERT INTO `articles` (`article_id`, `title`, `content`, `author_id`, `category_id`, `publication_date`, `is_published`) VALUES
(1, 'Quantum Computing: A Major Breakthrough', 'Scientists have achieved a new milestone in quantum stability.', 1, 1, '2025-11-25 16:33:49', 1),
(2, 'The New Smartphone Trends of 2025', 'Foldable screens are out, holographic displays are in.', 1, 1, '2025-11-25 16:33:49', 1),
(3, 'Market Rally Continues into Q4', 'Stock markets hit record highs as inflation data improves.', 3, 2, '2025-11-25 16:33:49', 1),
(4, 'Startups to Watch this Summer', 'Five new companies are disrupting the fintech industry.', 3, 2, '2025-11-25 16:33:49', 1),
(5, 'New Vitamin D Research', 'Studies suggest Vitamin D plays a large role in immune health.', 4, 3, '2025-11-25 16:33:49', 1),
(6, 'SpaceX Launches New Probe', 'The mission aims to explore the moons of Jupiter.', 8, 3, '2025-11-25 16:33:49', 1),
(7, 'Senate Passes New Infrastructure Bill', 'The bill passed 60-40, promising better roads.', 2, 4, '2025-11-25 16:33:49', 1),
(8, 'Election Year Predictions', 'Early polls suggest a tight race for the upcoming elections.', 2, 4, '2025-11-25 16:33:49', 1),
(9, 'Championship Finals Recap', 'The underdogs took home the trophy with a last-minute goal.', 7, 5, '2025-11-25 16:33:49', 1),
(10, 'Transfer Window Rumors', 'Top players are looking to move leagues next week.', 7, 5, '2025-11-25 16:33:49', 1),
(11, 'Blockbuster Movie Breaks Records', 'The latest superhero film shattered box office records.', 6, 6, '2025-11-25 16:33:49', 1),
(12, 'Celebrity Gala Highlights', 'A look at the best and worst dressed at the gala.', 6, 6, '2025-11-25 16:33:49', 1),
(13, 'Peace Treaty Signed in Summit', 'Leaders from three nations met today to sign the agreement.', 9, 7, '2025-11-25 16:33:49', 1),
(14, 'Climate Change Conference Begins', 'Delegates arrive to discuss carbon emission targets.', 9, 7, '2025-11-25 16:33:49', 1),
(15, '10 Tips for a Better Work-Life Balance', 'Here are ten ways to manage your stress.', 10, 3, '2025-11-25 16:33:49', 1),
(16, 'Why Remote Work is Here to Stay', 'Companies are realizing office leases are expensive.', 3, 2, '2025-11-25 16:33:49', 1),
(17, 'The Rise of Indie Game Developers', 'Small studios are creating impactful games.', 1, 1, '2025-11-25 16:33:49', 1),
(18, 'Local Hero Saves Cat from Tree', 'A local firefighter rescued a kitten stuck for two days.', 10, 6, '2025-11-25 16:33:49', 1),
(19, 'Diet Myths Debunked', 'Why cutting carbs completely might not be the best idea.', 4, 3, '2025-11-25 16:33:49', 1),
(21, 'Technologia', 'Ai is very good for cheating,everyone should ues ai evryday', 11, 1, '2025-11-25 18:12:46', 1),
(22, 'marzan', 'marzan is a brand of entertainment', 11, 6, '2025-11-26 14:29:03', 1);

-- --------------------------------------------------------

--
-- Table structure for table `authors`
--

CREATE TABLE `authors` (
  `author_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `bio` text DEFAULT NULL,
  `registration_date` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `authors`
--

INSERT INTO `authors` (`author_id`, `name`, `email`, `bio`, `registration_date`) VALUES
(1, 'Alice Johnson', 'new_email@news.com', 'Senior Tech Correspondent covering AI and silicon valley.', '2025-11-25 16:33:49'),
(2, 'Bob Smith', 'bob@news.com', 'Political analyst with 20 years of experience.', '2025-11-25 16:33:49'),
(3, 'Charlie Davis', 'charlie@news.com', 'Financial expert focusing on global markets.', '2025-11-25 16:33:49'),
(4, 'Diana Evans', 'diana@news.com', 'Health reporter and former medical practitioner.', '2025-11-25 16:33:49'),
(5, 'Ethan Hunt', 'ethan@news.com', 'Investigative journalist looking for the hard truths.', '2025-11-25 16:33:49'),
(6, 'Fiona Green', 'fiona@news.com', 'Entertainment critic and movie reviewer.', '2025-11-25 16:33:49'),
(7, 'George Baker', 'george@news.com', 'Sports commentator specializing in football and basketball.', '2025-11-25 16:33:49'),
(8, 'Hannah Lee', 'hannah@news.com', 'Science editor fascinated by space exploration.', '2025-11-25 16:33:49'),
(9, 'Ian Clark', 'ian@news.com', 'Covering international relations and diplomacy.', '2025-11-25 16:33:49'),
(10, 'Julia White', 'julia@news.com', 'Opinion columnist and lifestyle blogger.', '2025-11-25 16:33:49'),
(11, 'opc', 'opc@gmail.com', '', '2025-11-25 18:07:47');

-- --------------------------------------------------------

--
-- Table structure for table `categories`
--

CREATE TABLE `categories` (
  `category_id` int(11) NOT NULL,
  `category_name` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `categories`
--

INSERT INTO `categories` (`category_id`, `category_name`) VALUES
(2, 'Business'),
(6, 'Entertainment'),
(3, 'Health & Science'),
(4, 'Politics'),
(5, 'Sports'),
(1, 'Technology'),
(7, 'World News');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `articles`
--
ALTER TABLE `articles`
  ADD PRIMARY KEY (`article_id`),
  ADD KEY `author_id` (`author_id`),
  ADD KEY `category_id` (`category_id`);

--
-- Indexes for table `authors`
--
ALTER TABLE `authors`
  ADD PRIMARY KEY (`author_id`),
  ADD UNIQUE KEY `name` (`name`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `categories`
--
ALTER TABLE `categories`
  ADD PRIMARY KEY (`category_id`),
  ADD UNIQUE KEY `category_name` (`category_name`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `articles`
--
ALTER TABLE `articles`
  MODIFY `article_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- AUTO_INCREMENT for table `authors`
--
ALTER TABLE `authors`
  MODIFY `author_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `categories`
--
ALTER TABLE `categories`
  MODIFY `category_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `articles`
--
ALTER TABLE `articles`
  ADD CONSTRAINT `articles_ibfk_1` FOREIGN KEY (`author_id`) REFERENCES `authors` (`author_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `articles_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
