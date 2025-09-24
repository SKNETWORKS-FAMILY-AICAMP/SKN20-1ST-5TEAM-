-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema 1st_project
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema 1st_project
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `1st_project` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `1st_project` ;

-- -----------------------------------------------------
-- Table `1st_project`.`dim_monthly`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `1st_project`.`dim_monthly` (
  `date_key` INT NOT NULL,
  `year` INT NOT NULL,
  `month` INT NOT NULL,
  PRIMARY KEY (`date_key`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `1st_project`.`eco_monthly`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `1st_project`.`eco_monthly` (
  `date_key` INT NOT NULL,
  `ev` INT NOT NULL,
  `cng` INT NOT NULL,
  `hev` INT NOT NULL,
  `fcev` INT NOT NULL,
  `etc` INT NOT NULL,
  PRIMARY KEY (`date_key`),
  CONSTRAINT `fk_eco_monthly_dim_month`
    FOREIGN KEY (`date_key`)
    REFERENCES `1st_project`.`dim_monthly` (`date_key`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `1st_project`.`faq`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `1st_project`.`faq` (
  `idfaq` INT NOT NULL AUTO_INCREMENT,
  `company` VARCHAR(45) NOT NULL,
  `question` VARCHAR(500) NOT NULL,
  `answer` LONGTEXT NOT NULL,
  PRIMARY KEY (`idfaq`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `1st_project`.`ice_monthly`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `1st_project`.`ice_monthly` (
  `date_key` INT NOT NULL,
  `gasoline` INT NOT NULL,
  `diesel` INT NOT NULL,
  `lpg` INT NOT NULL,
  PRIMARY KEY (`date_key`),
  CONSTRAINT `fk_ice_monthly_dim_month1`
    FOREIGN KEY (`date_key`)
    REFERENCES `1st_project`.`dim_monthly` (`date_key`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;