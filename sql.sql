-- MySQL Script - Schema AyDS

DROP DATABASE AyDS;

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, 
SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

CREATE SCHEMA IF NOT EXISTS `AyDS` DEFAULT CHARACTER SET utf8;
USE `AyDS`;

-- -----------------------------------------------------
-- ROLES
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `roles` (
  `idroles` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`idroles`),
  UNIQUE (`nombre`)
) ENGINE=InnoDB;

INSERT INTO `roles` (`nombre`) VALUES
('Alumno'),('Administrador');

-- -----------------------------------------------------
-- PREGUNTAS DE RECUPERACION
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `preguntas_recuperacion` (
  `idrecuperacion` INT NOT NULL AUTO_INCREMENT,
  `pregunta` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`idrecuperacion`)
) ENGINE=InnoDB;

INSERT INTO `preguntas_recuperacion` (`pregunta`) VALUES 
('En donde naciste?'),
('Nombre de tu personaje favorito?'),
('Nombre de tu primera mascota?'),
('Nombre de tu mejor amigo?'), 
('Comida favorita?');

-- -----------------------------------------------------
-- USUARIO
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `usuario` (
  `boleta` VARCHAR(45) NOT NULL,
  `nombre` VARCHAR(100) NOT NULL,
  `contrasena` VARCHAR(256) NOT NULL,
  `res_recu` VARCHAR(45) NOT NULL,
  `idrecuperacion` INT NOT NULL,
  `roles_idroles` INT NOT NULL,

  PRIMARY KEY (`boleta`),
  INDEX (`roles_idroles`),
  INDEX (`idrecuperacion`),

  CONSTRAINT `fk_usuario_roles`
    FOREIGN KEY (`roles_idroles`)
    REFERENCES `roles` (`idroles`),

  CONSTRAINT `fk_usuario_preguntas`
    FOREIGN KEY (`idrecuperacion`)
    REFERENCES `preguntas_recuperacion` (`idrecuperacion`)
) ENGINE=InnoDB;

INSERT INTO `usuario`
(`boleta`, `nombre`, `contrasena`, `res_recu`, `idrecuperacion`, `roles_idroles`)
VALUES
('0', 'admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'admin', 1, 2),
('2025670127', 'Christian Manuel Sánchez Flores', 'b221d9dbb083a7f33428d7c2a3c3198ae925614d70210e28716ccaa7cd4ddb79', 'zacatecas', 1, 1);

-- -----------------------------------------------------
-- MATERIAS
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `materias` (
  `idmaterias` INT NOT NULL AUTO_INCREMENT,
  `usuario_boleta` VARCHAR(45) NOT NULL,
  `semestre` INT NOT NULL,
  `nombre` VARCHAR(45) NOT NULL,

  PRIMARY KEY (`idmaterias`),
  INDEX (`usuario_boleta`),

  CONSTRAINT `fk_materias_usuario`
    FOREIGN KEY (`usuario_boleta`)
    REFERENCES `usuario` (`boleta`)
) ENGINE=InnoDB;

-- ejemplo de inserción válida
INSERT INTO `materias` (`usuario_boleta`, `semestre`, `nombre`)
VALUES ('0', '1', 'Matematicas'),
('2025670127', '1', 'Desarrollo Web'),
('2025670127', '1', 'Probabilidad y Estadística');


-- -----------------------------------------------------
-- QUIZ BASE
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `quiz_base` (
  `usuario_boleta` VARCHAR(45) NOT NULL,
  `grupo` VARCHAR(45) NOT NULL,
  `carrera` VARCHAR(45) NOT NULL,
  `universidad` VARCHAR(45) NOT NULL,
  `sit_acad` VARCHAR(45) NOT NULL,
  `semestre` INT NOT NULL DEFAULT 1,
  `propenso_estres` INT NOT NULL,
  `aplicado` BOOLEAN NOT NULL DEFAULT FALSE,
  `fecha_aplicacion` DATE,

  PRIMARY KEY (`usuario_boleta`),
  INDEX (`usuario_boleta`),

  CONSTRAINT `fk_quiz_usuario`
    FOREIGN KEY (`usuario_boleta`)
    REFERENCES `usuario` (`boleta`)
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- ACTIVIDADES
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `actividades` (
  `id_act` INT NOT NULL AUTO_INCREMENT,
  `usuario_boleta` VARCHAR(45) NOT NULL,
  `materias_idmaterias` INT NOT NULL,
  `nombre` VARCHAR(45) NOT NULL,
  `descripcion` VARCHAR(255),
  `fecha_entrega` DATETIME NOT NULL,
  `prioridad` INT NOT NULL,
  `semestre` INT NOT NULL,
  `estado` VARCHAR(45) NOT NULL DEFAULT FALSE,

  PRIMARY KEY (`id_act`),
  INDEX (`usuario_boleta`),
  INDEX (`materias_idmaterias`),

  CONSTRAINT `fk_act_usuario`
    FOREIGN KEY (`usuario_boleta`)
    REFERENCES `usuario` (`boleta`),

  CONSTRAINT `fk_act_materia`
    FOREIGN KEY (`materias_idmaterias`)
    REFERENCES `materias` (`idmaterias`)
) ENGINE=InnoDB;