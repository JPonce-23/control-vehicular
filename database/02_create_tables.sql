-- ============================================
-- Sistema de Control Vehicular
-- Script de creación de tablas
-- Base de datos: control_vehicular
-- ============================================

-- ============================================
-- ENUMS
-- ============================================

-- Aquí se crearán los tipos de datos controlados.

CREATE TYPE rol_usuario AS ENUM ('administrador', 'capturista');