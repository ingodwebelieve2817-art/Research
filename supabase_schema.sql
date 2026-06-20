-- ==========================================
-- SUPABASE POSTGRESQL DATABASE SCHEMA
-- ==========================================
-- This file contains SQL DDL statements for the tables representing Users, Customers,
-- Projects, and Activities, along with indices, constraints, and a trigger to sync
-- Supabase Auth users with Django accounts.
-- Run these scripts in the Supabase SQL Editor.

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- -------------------------------------------------------------
-- 1. USERS TABLE (maps to accounts_user Django model)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.accounts_user (
    id bigserial PRIMARY KEY,
    password varchar(128) NOT NULL,
    last_login timestamptz,
    is_superuser boolean NOT NULL DEFAULT false,
    username varchar(150) UNIQUE NOT NULL,
    first_name varchar(150) NOT NULL DEFAULT '',
    last_name varchar(150) NOT NULL DEFAULT '',
    email varchar(254) NOT NULL DEFAULT '',
    is_staff boolean NOT NULL DEFAULT false,
    is_active boolean NOT NULL DEFAULT true,
    date_joined timestamptz NOT NULL DEFAULT now(),
    phone varchar(20) NOT NULL DEFAULT '',
    avatar varchar(100), -- image file path/URL
    supabase_uid uuid UNIQUE, -- foreign reference to auth.users (UUID)
    created_at timestamptz NOT NULL DEFAULT now()
);

-- Index for searching users by email or Supabase UID
CREATE INDEX IF NOT EXISTS idx_accounts_user_supabase_uid ON public.accounts_user (supabase_uid);
CREATE INDEX IF NOT EXISTS idx_accounts_user_email ON public.accounts_user (email);

-- -------------------------------------------------------------
-- 2. CUSTOMERS TABLE (maps to customers_customer Django model)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.customers_customer (
    id bigserial PRIMARY KEY,
    name varchar(200) NOT NULL,
    phone varchar(20) UNIQUE NOT NULL,
    whatsapp_number varchar(20) NOT NULL DEFAULT '',
    city varchar(100) NOT NULL,
    opted_in_whatsapp boolean NOT NULL DEFAULT true,
    opted_in_facebook boolean NOT NULL DEFAULT false,
    is_active boolean NOT NULL DEFAULT true,
    added_at timestamptz NOT NULL DEFAULT now()
);

-- Indices for customer searching & matching
CREATE INDEX IF NOT EXISTS idx_customers_city ON public.customers_customer (city);
CREATE INDEX IF NOT EXISTS idx_customers_name ON public.customers_customer (name);

-- -------------------------------------------------------------
-- 3. PROJECTS TABLE (maps to projects_project Django model)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.projects_project (
    id bigserial PRIMARY KEY,
    name varchar(255) NOT NULL,
    description text NOT NULL DEFAULT '',
    status varchar(50) NOT NULL DEFAULT 'pending',
    budget numeric(12, 2),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    
    -- Relationships
    provider_id bigint NOT NULL, -- references services_serviceprovider(id)
    customer_id bigint,          -- references customers_customer(id)
    
    -- Constraints
    CONSTRAINT chk_project_status CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    CONSTRAINT fk_project_customer FOREIGN KEY (customer_id) REFERENCES public.customers_customer(id) ON DELETE SET NULL
);

-- Indices for project queries
CREATE INDEX IF NOT EXISTS idx_projects_provider_status ON public.projects_project (provider_id, status);
CREATE INDEX IF NOT EXISTS idx_projects_customer ON public.projects_project (customer_id);

-- -------------------------------------------------------------
-- 4. ACTIVITIES LOG TABLE (maps to activities_activitylog Django model)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.activities_activitylog (
    id bigserial PRIMARY KEY,
    action varchar(255) NOT NULL,
    details text NOT NULL DEFAULT '',
    created_at timestamptz NOT NULL DEFAULT now(),
    
    -- Relationship to User
    user_id bigint NOT NULL,
    
    -- Constraints
    CONSTRAINT fk_activity_user FOREIGN KEY (user_id) REFERENCES public.accounts_user(id) ON DELETE CASCADE
);

-- Indices for activities timeline views
CREATE INDEX IF NOT EXISTS idx_activities_user_created ON public.activities_activitylog (user_id, created_at DESC);

-- =============================================================
-- AUTOMATIC SYNC FROM SUPABASE AUTH TO DJANGO USERS TABLE
-- =============================================================
-- This function automatically creates a record in public.accounts_user
-- when a new user signs up via Supabase Auth.

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.accounts_user (
    supabase_uid,
    username,
    email,
    phone,
    is_active,
    is_staff,
    is_superuser,
    date_joined
  )
  VALUES (
    new.id,
    new.email,
    new.email,
    coalesce(new.phone, ''),
    true,
    false,
    false,
    now()
  );
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to execute on signup
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
