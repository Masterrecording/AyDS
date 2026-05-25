-- MySQL Script - Schema AyDS
-- Versión corregida 1.1

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

CREATE SCHEMA IF NOT EXISTS `AyDS` DEFAULT CHARACTER SET utf8;
USE `AyDS`;

-- NO LO DESCOMENTEN
-- Y MUCHO MENOS LO EJECUTEN
-- !!!!!!!!!!!!!!!!!!!!!!
-- !!!!! POR FAVOR !!!!!!
-- !!!!!!!!!!!!!!!!!!!!!!
-- drop database AyDS;

-- -----------------------------------------------------
-- roles
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `AyDS`.`roles` (
  `idroles`  INT         NOT NULL AUTO_INCREMENT,
  `nombre`   VARCHAR(20) NOT NULL,
  PRIMARY KEY (`idroles`),
  UNIQUE INDEX `nombre_UNIQUE` (`nombre` ASC)
) ENGINE = InnoDB;

INSERT INTO roles (nombre) VALUES
('Alumno'),('Administrador');


-- -----------------------------------------------------
-- Table `AyDS`.`preguntas_recuperacion`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `AyDS`.`preguntas_recuperacion` (
  `idrecuperacion` INT NOT NULL AUTO_INCREMENT,
  `pregunta`       VARCHAR(45) NOT NULL,
  PRIMARY KEY (`idrecuperacion`)
) ENGINE = InnoDB;

INSERT INTO `preguntas_recuperacion` (`pregunta`) VALUES 
('En dónde naciste?'),
('Nombre de tu personaje favorito?'),
('Nombre de tu primera mascota?'),
('Nombre de tu mejor amigo?'),
('Comida favorita?');

-- -----------------------------------------------------
-- usuario
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `AyDS`.`usuario` (
  `idusuario`      INT          NOT NULL AUTO_INCREMENT,
  `nombre`         VARCHAR(45)  NOT NULL,
  `boleta`         VARCHAR(45)  NOT NULL,
  `contraseña`     VARCHAR(256) NOT NULL,
  `res_recu`       VARCHAR(45)  NOT NULL,
  `idrecuperacion` INT          NOT NULL,
  `roles_idroles`  INT          NOT NULL,
  PRIMARY KEY (`idusuario`),
  INDEX `fk_usuario_roles_idx` (`roles_idroles` ASC),
  INDEX `fk_usuario_preguntas_recuperacion_idx` (`idrecuperacion` ASC),
  CONSTRAINT `fk_usuario_roles`
    FOREIGN KEY (`roles_idroles`)
    REFERENCES `AyDS`.`roles` (`idroles`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_usuario_preguntas_recuperacion`
    FOREIGN KEY (`idrecuperacion`)
    REFERENCES `AyDS`.`preguntas_recuperacion` (`idrecuperacion`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE = InnoDB;

INSERT INTO `AyDS`.`usuario` (`nombre`, `boleta`, `contraseña`, `res_recu`, `idrecuperacion`, `roles_idroles`)
VALUES ('admin', 0, '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'admin', 1, 2);

-- -----------------------------------------------------
-- carreras
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `AyDS`.`carreras` (
  `idcarreras`  INT         NOT NULL AUTO_INCREMENT,
  `nombre`      VARCHAR(45) NOT NULL,
  PRIMARY KEY (`idcarreras`)
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- materias
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `AyDS`.`materias` (
  `idmaterias`  INT         NOT NULL AUTO_INCREMENT,
  `nombre`      VARCHAR(45) NOT NULL,
  PRIMARY KEY (`idmaterias`)
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- docente
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `AyDS`.`docente` (
  `iddocente`           INT         NOT NULL AUTO_INCREMENT,
  `nombre`              VARCHAR(45) NOT NULL,
  `inf`                 INT         NOT NULL,
  `materias_idmaterias` INT         NOT NULL,
  PRIMARY KEY (`iddocente`),
  INDEX `fk_docente_materias1_idx` (`materias_idmaterias` ASC),
  CONSTRAINT `fk_docente_materias1`
    FOREIGN KEY (`materias_idmaterias`)
    REFERENCES `AyDS`.`materias` (`idmaterias`)
    ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- datos_usuario_perm
-- CORRECCIÓN: se eliminaron columnas redundantes
--   (`carrera` VARCHAR, `carrera_id` VARCHAR, `materias_id` VARCHAR)
--   que duplicaban información ya expresada por las FKs.
-- La carrera y materia principal del alumno se guardan aquí como FK.
-- `hobbies_horas` y `semestre` se mantienen porque son datos
--   permanentes/de perfil que no cambian por periodo.
-- CORRECCIÓN: se eliminó la FK duplicada `usuario_idusuario` 
--   (la PK `usuario_idusuario1` ya actúa como FK al usuario).
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `AyDS`.`datos_usuario_perm` (
  `usuario_idusuario`   INT         NOT NULL,
  `carreras_idcarreras` INT         NOT NULL,
  `hobbies_horas`       VARCHAR(45) NOT NULL,
  PRIMARY KEY (`usuario_idusuario`),
  INDEX `fk_datos_perm_carreras_idx` (`carreras_idcarreras` ASC),
  CONSTRAINT `fk_datos_perm_usuario`
    FOREIGN KEY (`usuario_idusuario`)
    REFERENCES `AyDS`.`usuario` (`idusuario`)
    ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_datos_perm_carreras`
    FOREIGN KEY (`carreras_idcarreras`)
    REFERENCES `AyDS`.`carreras` (`idcarreras`)
    ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- datos_usuario_temp
-- CORRECCIÓN: se agregó `fecha_inicio` para poder guardar
--   un registro por periodo sin sobrescribir el anterior.
--   La PK ahora es compuesta (usuario + fecha_inicio).
-- Se agrega FK a docente y a materias para reemplazar
--   los campos VARCHAR que antes guardaban esos IDs como texto.
-- `sit_acad`/`sir_acad` se unificó el nombre a `sit_acad`.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `AyDS`.`datos_usuario_temp` (
  `usuario_idusuario`    INT         NOT NULL,
  `fecha_inicio`         DATE        NOT NULL,
  `grupo`                VARCHAR(45) NOT NULL,
  `sit_acad`             VARCHAR(45) NOT NULL,
  `num_materias`         INT         NOT NULL,
  `semestre`             INT         NOT NULL,
  `str_tolerancia`       VARCHAR(45) NOT NULL,
  `perse_carga`          INT         NOT NULL,
  `materias_idmaterias`  INT         NOT NULL,
  `docente_iddocente`    INT         NOT NULL,
  PRIMARY KEY (`usuario_idusuario`, `fecha_inicio`),
  INDEX `fk_temp_materias_idx` (`materias_idmaterias` ASC),
  INDEX `fk_temp_docente_idx`  (`docente_iddocente` ASC),
  CONSTRAINT `fk_temp_usuario`
    FOREIGN KEY (`usuario_idusuario`)
    REFERENCES `AyDS`.`usuario` (`idusuario`)
    ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_temp_materias`
    FOREIGN KEY (`materias_idmaterias`)
    REFERENCES `AyDS`.`materias` (`idmaterias`)
    ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_temp_docente`
    FOREIGN KEY (`docente_iddocente`)
    REFERENCES `AyDS`.`docente` (`iddocente`)
    ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- Quiz_base_estado
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `AyDS`.`Quiz_base_estado` (
  `usuario_idusuario`  INT      NOT NULL,
  `aplicada`           TINYINT  NOT NULL,
  `fecha_aplicacion`   DATE     NOT NULL,
  PRIMARY KEY (`usuario_idusuario`),
  CONSTRAINT `fk_quiz_base_estado_usuario`
    FOREIGN KEY (`usuario_idusuario`)
    REFERENCES `AyDS`.`usuario` (`idusuario`)
    ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- quiz_seguimiento
-- Sin cambios — guarda la última aplicación del quiz
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `AyDS`.`quiz_seguimiento` (
  `usuario_idusuario`  INT   NOT NULL,
  `ultima_aplicacion`  DATE  NOT NULL,
  PRIMARY KEY (`usuario_idusuario`),
  CONSTRAINT `fk_quiz_seguimiento_usuario`
    FOREIGN KEY (`usuario_idusuario`)
    REFERENCES `AyDS`.`usuario` (`idusuario`)
    ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- quiz_base
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `AyDS`.`quiz_base` (
  `usuario_idusuario`   INT         NOT NULL,
  `grupo`               VARCHAR(45) NOT NULL,
  `sit_acad`            VARCHAR(45) NOT NULL,
  `num_materias`        INT         NOT NULL,
  `semestre`            INT         NOT NULL,
  `str_tolerancia`      VARCHAR(45) NOT NULL,
  `perse_carga`         INT         NOT NULL,
  `docente_iddocente`   INT         NOT NULL,
  `gruopo_relacion`     INT         NOT NULL,
  `pers_anim_general`   VARCHAR(45) NOT NULL,
  `motivacion_acad`     VARCHAR(45) NOT NULL,
  PRIMARY KEY (`usuario_idusuario`),
  INDEX `fk_quiz_base_docente_idx` (`docente_iddocente` ASC),
  CONSTRAINT `fk_quiz_base_estado`
    FOREIGN KEY (`usuario_idusuario`)
    REFERENCES `AyDS`.`Quiz_base_estado` (`usuario_idusuario`)
    ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_quiz_base_docente`
    FOREIGN KEY (`docente_iddocente`)
    REFERENCES `AyDS`.`docente` (`iddocente`)
    ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE = InnoDB;

-- =============================================================
-- ACTIVIDADES
-- Cada tabla guarda un registro por ocurrencia de la actividad.
-- `estado`: 'pendiente' al crear (preguntas "antes"),
--           'completada' al registrar las preguntas "después".
-- `tiempo_real` se llena solo al completar (puede ser NULL).
-- Las respuestas a preguntas cerradas se guardan como TINYINT
--   (0 = No, 1 = Sí) o INT para escalas numéricas.
-- =============================================================

-- -----------------------------------------------------
-- act_examen
-- Antes:  tiempo_estimado, temas_dificiles, genera_estres
-- Después: tiempo_real
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `AyDS`.`act_examen` (
  `idact_examen`        INT         NOT NULL AUTO_INCREMENT,
  `usuario_idusuario`   INT         NOT NULL,
  `materias_idmaterias` INT         NOT NULL,
  `fecha`               DATETIME    NOT NULL,
  `tiempo_estimado`     INT         NOT NULL COMMENT 'minutos estimados de estudio',
  `temas_dificiles`     INT     NOT NULL COMMENT '1:nada, 2:poco, 3:mas o menos, 4:bastante, 5:mucho',
  `genera_estres`       INT     NOT NULL COMMENT '1:nada, 2:poco, 3:mas o menos, 4:bastante, 5:mucho',
  `tiempo_real`         INT             NULL COMMENT 'minutos reales, se llena al completar',
  `estado`              VARCHAR(15) NOT NULL DEFAULT 'pendiente' COMMENT 'pendiente | completada',
  PRIMARY KEY (`idact_examen`),
  INDEX `fk_act_examen_usuario_idx`  (`usuario_idusuario` ASC),
  INDEX `fk_act_examen_materia_idx`  (`materias_idmaterias` ASC),
  CONSTRAINT `fk_act_examen_usuario`
    FOREIGN KEY (`usuario_idusuario`)
    REFERENCES `AyDS`.`usuario` (`idusuario`)
    ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_act_examen_materia`
    FOREIGN KEY (`materias_idmaterias`)
    REFERENCES `AyDS`.`materias` (`idmaterias`)
    ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- act_proyecto
-- Antes:  tiempo_estimado, complejo, en_equipo, genera_estres
-- Después: tiempo_real
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `AyDS`.`act_proyecto` (
  `idact_proyecto`      INT         NOT NULL AUTO_INCREMENT,
  `usuario_idusuario`   INT         NOT NULL,
  `materias_idmaterias` INT         NOT NULL,
  `fecha`               DATETIME    NOT NULL,
  `tiempo_estimado`     INT         NOT NULL COMMENT 'minutos estimados',
  `complejo`            INT     NOT NULL COMMENT '1:nada, 2:poco, 3:mas o menos, 4:bastante, 5:mucho',
  `en_equipo`           TINYINT     NOT NULL COMMENT '0=No 1=Si',
  `genera_estres`       INT     NOT NULL COMMENT '1:nada, 2:poco, 3:mas o menos, 4:bastante, 5:mucho',
  `tiempo_real`         INT             NULL COMMENT 'se llena al completar',
  `estado`              VARCHAR(15) NOT NULL DEFAULT 'pendiente',
  PRIMARY KEY (`idact_proyecto`),
  INDEX `fk_act_proyecto_usuario_idx` (`usuario_idusuario` ASC),
  INDEX `fk_act_proyecto_materia_idx` (`materias_idmaterias` ASC),
  CONSTRAINT `fk_act_proyecto_usuario`
    FOREIGN KEY (`usuario_idusuario`)
    REFERENCES `AyDS`.`usuario` (`idusuario`)
    ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_act_proyecto_materia`
    FOREIGN KEY (`materias_idmaterias`)
    REFERENCES `AyDS`.`materias` (`idmaterias`)
    ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- act_equipo
-- Solo tiene preguntas "en el momento" (sin antes/después)
-- `funcionamiento_equipo`: escala 1-5
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `AyDS`.`act_equipo` (
  `idact_equipo`        INT         NOT NULL AUTO_INCREMENT,
  `usuario_idusuario`   INT         NOT NULL,
  `materias_idmaterias` INT         NOT NULL,
  `fecha`               DATETIME    NOT NULL,
  `comodo_equipo`       INT     NOT NULL COMMENT '1:nada, 2:poco, 3:mas o menos, 4:bastante, 5:mucho',
  `funcionamiento`      INT         NOT NULL COMMENT 'escala 1-5',
  `estado`              VARCHAR(15) NOT NULL DEFAULT 'completada',
  PRIMARY KEY (`idact_equipo`),
  INDEX `fk_act_equipo_usuario_idx` (`usuario_idusuario` ASC),
  INDEX `fk_act_equipo_materia_idx` (`materias_idmaterias` ASC),
  CONSTRAINT `fk_act_equipo_usuario`
    FOREIGN KEY (`usuario_idusuario`)
    REFERENCES `AyDS`.`usuario` (`idusuario`)
    ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_act_equipo_materia`
    FOREIGN KEY (`materias_idmaterias`)
    REFERENCES `AyDS`.`materias` (`idmaterias`)
    ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- act_tarea
-- Antes:  tiempo_estimado, compleja, instrucciones_claras
-- Después: tiempo_real
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `AyDS`.`act_tarea` (
  `idact_tarea`         INT         NOT NULL AUTO_INCREMENT,
  `usuario_idusuario`   INT         NOT NULL,
  `materias_idmaterias` INT         NOT NULL,
  `fecha`               DATETIME    NOT NULL,
  `tiempo_estimado`     INT         NOT NULL COMMENT 'minutos estimados',
  `compleja`            INT     NOT NULL COMMENT '1:nada, 2:poco, 3:mas o menos, 4:bastante, 5:mucho',
  `instrucciones_claras` TINYINT    NOT NULL COMMENT '0=No 1=Si',
  `tiempo_real`         INT             NULL COMMENT 'se llena al completar',
  `estado`              VARCHAR(15) NOT NULL DEFAULT 'pendiente',
  PRIMARY KEY (`idact_tarea`),
  INDEX `fk_act_tarea_usuario_idx` (`usuario_idusuario` ASC),
  INDEX `fk_act_tarea_materia_idx` (`materias_idmaterias` ASC),
  CONSTRAINT `fk_act_tarea_usuario`
    FOREIGN KEY (`usuario_idusuario`)
    REFERENCES `AyDS`.`usuario` (`idusuario`)
    ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_act_tarea_materia`
    FOREIGN KEY (`materias_idmaterias`)
    REFERENCES `AyDS`.`materias` (`idmaterias`)
    ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE = InnoDB;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;