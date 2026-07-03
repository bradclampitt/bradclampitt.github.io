-- Unified Database Schema
-- All tables are namespaced by section to maintain clear separation
-- This schema combines all section schemas into a single database

PRAGMA foreign_keys = ON;

-- ============================================================================
-- BLOG SECTION
-- ============================================================================

CREATE TABLE IF NOT EXISTS blog_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    label TEXT NOT NULL,
    description TEXT,
    icon TEXT,
    display_order INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS blog_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    excerpt TEXT,
    content_markdown TEXT NOT NULL,
    content_html TEXT NOT NULL,
    author TEXT DEFAULT 'Bradley R. Clampitt',
    date TEXT NOT NULL,
    category_id INTEGER,
    tags TEXT, -- JSON array stored as text
    featured INTEGER DEFAULT 0,
    read_time TEXT,
    cover_image TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    status TEXT DEFAULT 'Published',
    FOREIGN KEY (category_id) REFERENCES blog_categories(id)
);

CREATE INDEX IF NOT EXISTS idx_blog_posts_slug ON blog_posts(slug);
CREATE INDEX IF NOT EXISTS idx_blog_posts_date ON blog_posts(date DESC);
CREATE INDEX IF NOT EXISTS idx_blog_posts_category_id ON blog_posts(category_id);
CREATE INDEX IF NOT EXISTS idx_blog_posts_featured ON blog_posts(featured);
CREATE INDEX IF NOT EXISTS idx_blog_categories_code ON blog_categories(code);
CREATE INDEX IF NOT EXISTS idx_blog_categories_display_order ON blog_categories(display_order);

-- ============================================================================
-- DOCUMENTS SECTION
-- ============================================================================

CREATE TABLE IF NOT EXISTS doc_categories (
  id          INTEGER PRIMARY KEY,
  code        TEXT UNIQUE NOT NULL,
  label       TEXT NOT NULL,
  description TEXT,
  icon        TEXT,
  sort        INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS doc_types (
  id          INTEGER PRIMARY KEY,
  code        TEXT UNIQUE NOT NULL,
  label       TEXT NOT NULL,
  description TEXT,
  icon        TEXT,
  sort        INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS doc_tabs (
  id    INTEGER PRIMARY KEY,
  code  TEXT UNIQUE NOT NULL,
  label TEXT NOT NULL,
  sort  INTEGER DEFAULT 0
);

INSERT OR IGNORE INTO doc_tabs (code, label, sort) VALUES
('all',            'All',            0),
('articles',       'Articles',      1),
('kbase',          'KBase',         2),
('guides',         'Guides',        3),
('tutorials',      'Tutorials',     4),
('troubleshooting', 'Troubleshooting', 5),
('architecture',   'Architecture',  6),
('others',         'Others',        7),
('dev-docs',       'Dev Docs',      8);

CREATE TABLE IF NOT EXISTS documents (
  id              INTEGER PRIMARY KEY,
  category_id     INTEGER REFERENCES doc_categories(id),
  type_id         INTEGER REFERENCES doc_types(id),
  title           TEXT NOT NULL,
  slug            TEXT UNIQUE,
  summary         TEXT,
  content_format  TEXT DEFAULT 'markdown',
  content_source  TEXT DEFAULT 'inline',
  content_path    TEXT,
  content_markdown TEXT,
  content_html    TEXT,
  created_at      TEXT,
  posted_at       TEXT,
  updated_at      TEXT,
  effective_from  TEXT,
  effective_to    TEXT,
  tags            TEXT,
  extra           JSON,
  status          TEXT DEFAULT 'Published',
  featured        INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS document_tabs (
  document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  tab_id      INTEGER NOT NULL REFERENCES doc_tabs(id),
  PRIMARY KEY (document_id, tab_id)
);

CREATE TABLE IF NOT EXISTS document_images (
  id          INTEGER PRIMARY KEY,
  document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
  url         TEXT NOT NULL,
  alt         TEXT,
  width       INTEGER,
  height      INTEGER,
  is_cover    INTEGER DEFAULT 0,
  sort        INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS document_links (
  id          INTEGER PRIMARY KEY,
  document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
  label       TEXT,
  url         TEXT,
  sort        INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_documents_slug       ON documents(slug);
CREATE INDEX IF NOT EXISTS idx_documents_dates      ON documents(created_at, posted_at, updated_at);
CREATE INDEX IF NOT EXISTS idx_documents_status     ON documents(status);
CREATE INDEX IF NOT EXISTS idx_document_tabs_tab    ON document_tabs(tab_id);
CREATE INDEX IF NOT EXISTS idx_images_document      ON document_images(document_id);
CREATE INDEX IF NOT EXISTS idx_links_document       ON document_links(document_id);
CREATE INDEX IF NOT EXISTS idx_categories_sort      ON doc_categories(sort);
CREATE INDEX IF NOT EXISTS idx_types_sort           ON doc_types(sort);
CREATE INDEX IF NOT EXISTS idx_tabs_sort            ON doc_tabs(sort);

-- ============================================================================
-- PORTFOLIO SECTION
-- ============================================================================

CREATE TABLE IF NOT EXISTS portfolio_clients (
  id        INTEGER PRIMARY KEY,
  name      TEXT NOT NULL,
  website   TEXT,
  logo_url  TEXT,
  blurb     TEXT
);

CREATE TABLE IF NOT EXISTS portfolio_project_types (
  id    INTEGER PRIMARY KEY,
  code  TEXT UNIQUE NOT NULL,
  label TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS portfolio_tabs (
  id    INTEGER PRIMARY KEY,
  code  TEXT UNIQUE NOT NULL,
  label TEXT NOT NULL,
  sort  INTEGER DEFAULT 0
);

INSERT OR IGNORE INTO portfolio_tabs (code, label, sort) VALUES
('all',        'All',        0),
('ecommerce',  'eCommerce',  1),
('corporate',  'Corporate',  2),
('personal',   'Personal',   3),
('future',     'Future',     4),
('community',  'Community',  5);

CREATE TABLE IF NOT EXISTS portfolio_projects (
  id              INTEGER PRIMARY KEY,
  client_id       INTEGER REFERENCES portfolio_clients(id),
  type_id         INTEGER REFERENCES portfolio_project_types(id),
  title           TEXT NOT NULL,
  slug            TEXT UNIQUE,
  summary         TEXT,
  description_html TEXT,
  launched_date   TEXT,
  posted_at       TEXT,
  updated_at      TEXT,
  in_use_start    TEXT,
  in_use_end      TEXT,
  tags            TEXT,
  extra           JSON
);

CREATE TABLE IF NOT EXISTS portfolio_project_tabs (
  project_id INTEGER NOT NULL REFERENCES portfolio_projects(id),
  tab_id     INTEGER NOT NULL REFERENCES portfolio_tabs(id),
  PRIMARY KEY (project_id, tab_id)
);

CREATE TABLE IF NOT EXISTS portfolio_project_images (
  id         INTEGER PRIMARY KEY,
  project_id INTEGER REFERENCES portfolio_projects(id),
  url        TEXT NOT NULL,
  alt        TEXT,
  width      INTEGER,
  height     INTEGER,
  is_cover   INTEGER DEFAULT 0,
  sort       INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS portfolio_project_links (
  id         INTEGER PRIMARY KEY,
  project_id INTEGER REFERENCES portfolio_projects(id),
  label      TEXT,
  url        TEXT,
  sort       INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS portfolio_project_features (
  id          INTEGER PRIMARY KEY,
  project_id  INTEGER NOT NULL REFERENCES portfolio_projects(id) ON DELETE CASCADE,
  label       TEXT NOT NULL,
  icon        TEXT,
  description TEXT,
  sort        INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS feature_library (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  label TEXT NOT NULL,
  icon TEXT,
  description TEXT,
  category TEXT
);

CREATE TABLE IF NOT EXISTS portfolio_feature_library (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  label TEXT NOT NULL,
  icon TEXT,
  description TEXT,
  category TEXT
);

CREATE TABLE IF NOT EXISTS portfolio_project_statuses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  label TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS portfolio_tech_tags (
  id       INTEGER PRIMARY KEY,
  code     TEXT UNIQUE NOT NULL,
  label    TEXT NOT NULL,
  icon     TEXT,
  category TEXT
);

CREATE TABLE IF NOT EXISTS portfolio_project_tech_tags (
  project_id INTEGER NOT NULL REFERENCES portfolio_projects(id) ON DELETE CASCADE,
  tag_id     INTEGER NOT NULL REFERENCES portfolio_tech_tags(id) ON DELETE CASCADE,
  PRIMARY KEY (project_id, tag_id)
);

CREATE INDEX IF NOT EXISTS idx_portfolio_projects_slug       ON portfolio_projects(slug);
CREATE INDEX IF NOT EXISTS idx_portfolio_projects_dates      ON portfolio_projects(launched_date, posted_at, updated_at);
CREATE INDEX IF NOT EXISTS idx_portfolio_images_project      ON portfolio_project_images(project_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_features_project    ON portfolio_project_features(project_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_project_tabs_tab    ON portfolio_project_tabs(tab_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_project_tech_proj   ON portfolio_project_tech_tags(project_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_project_tech_tag    ON portfolio_project_tech_tags(tag_id);

-- ============================================================================
-- REFERENCES SECTION
-- ============================================================================

CREATE TABLE IF NOT EXISTS ref_entries (
  id              INTEGER PRIMARY KEY,
  person_name     TEXT NOT NULL,
  company         TEXT,
  connection_type TEXT,
  reference_text  TEXT NOT NULL,
  title           TEXT,
  created_at      TEXT DEFAULT (datetime('now')),
  updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_ref_entries_person_name ON ref_entries(person_name);
CREATE INDEX IF NOT EXISTS idx_ref_entries_company ON ref_entries(company);
CREATE INDEX IF NOT EXISTS idx_ref_entries_created_at ON ref_entries(created_at);

-- ============================================================================
-- TECH SKILLS SECTION
-- ============================================================================

CREATE TABLE IF NOT EXISTS tech_skill_categories (
  id              INTEGER PRIMARY KEY,
  name            TEXT NOT NULL UNIQUE,
  display_order   INTEGER NOT NULL DEFAULT 0,
  created_at      TEXT DEFAULT (datetime('now')),
  updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS tech_skills (
  id              INTEGER PRIMARY KEY,
  skill_name      TEXT NOT NULL,
  logo_url        TEXT,
  description     TEXT,
  skill_level     TEXT NOT NULL,
  years_usage     TEXT,
  num_projects    TEXT,
  category_id     INTEGER NOT NULL,
  created_at      TEXT DEFAULT (datetime('now')),
  updated_at      TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (category_id) REFERENCES tech_skill_categories(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_tech_skills_name ON tech_skills(skill_name);
CREATE INDEX IF NOT EXISTS idx_tech_skills_category_id ON tech_skills(category_id);
CREATE INDEX IF NOT EXISTS idx_tech_skills_level ON tech_skills(skill_level);
CREATE INDEX IF NOT EXISTS idx_tech_skills_created_at ON tech_skills(created_at);
CREATE INDEX IF NOT EXISTS idx_tech_skill_categories_display_order ON tech_skill_categories(display_order);

-- ============================================================================
-- SIDE PROJECTS SECTION
-- ============================================================================

CREATE TABLE IF NOT EXISTS side_project_categories (
  id              INTEGER PRIMARY KEY,
  code            TEXT UNIQUE NOT NULL,
  label           TEXT NOT NULL,
  description     TEXT,
  color           TEXT,
  icon            TEXT,
  display_order   INTEGER DEFAULT 0,
  created_at      TEXT DEFAULT (datetime('now')),
  updated_at      TEXT DEFAULT (datetime('now'))
);

INSERT OR IGNORE INTO side_project_categories (code, label, description, color, icon, display_order) VALUES
('development', 'Development', 'Software development projects', 'blue', 'fas fa-code', 1),
('sysops', 'SysOps', 'System operations and infrastructure projects', 'red', 'fas fa-cogs', 2),
('hobbies', 'Hobbies', 'Personal hobby projects', 'green', 'fas fa-leaf', 3),
('electrical', 'Electrical', 'Electrical and home automation projects', 'yellow', 'fas fa-bolt', 4),
('diy', 'DIY', 'Do-it-yourself projects', 'purple', 'fas fa-tools', 5);

CREATE TABLE IF NOT EXISTS side_projects (
  id              INTEGER PRIMARY KEY,
  category_id     INTEGER REFERENCES side_project_categories(id) ON DELETE RESTRICT,
  title           TEXT NOT NULL,
  slug            TEXT UNIQUE,
  description     TEXT,
  status          TEXT DEFAULT 'in development',
  metrics         TEXT,
  posted_date     TEXT,
  revised_date    TEXT,
  stats           TEXT,
  created_at      TEXT DEFAULT (datetime('now')),
  updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS side_project_technologies (
  id              INTEGER PRIMARY KEY,
  project_id      INTEGER REFERENCES side_projects(id) ON DELETE CASCADE,
  name            TEXT NOT NULL,
  icon            TEXT,
  display_order   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS side_project_features (
  id              INTEGER PRIMARY KEY,
  project_id      INTEGER REFERENCES side_projects(id) ON DELETE CASCADE,
  name            TEXT NOT NULL,
  description     TEXT,
  icon            TEXT,
  display_order   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS side_project_technical_details (
  id              INTEGER PRIMARY KEY,
  project_id      INTEGER REFERENCES side_projects(id) ON DELETE CASCADE,
  title           TEXT NOT NULL,
  description     TEXT NOT NULL,
  display_order   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS side_project_images (
  id              INTEGER PRIMARY KEY,
  project_id      INTEGER REFERENCES side_projects(id) ON DELETE CASCADE,
  url             TEXT NOT NULL,
  alt             TEXT,
  width           INTEGER,
  height          INTEGER,
  is_cover        INTEGER DEFAULT 0,
  display_order   INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_side_projects_category ON side_projects(category_id);
CREATE INDEX IF NOT EXISTS idx_side_projects_slug ON side_projects(slug);
CREATE INDEX IF NOT EXISTS idx_side_projects_status ON side_projects(status);
CREATE INDEX IF NOT EXISTS idx_side_projects_posted_date ON side_projects(posted_date);
CREATE INDEX IF NOT EXISTS idx_side_projects_revised_date ON side_projects(revised_date);
CREATE INDEX IF NOT EXISTS idx_side_project_technologies_project ON side_project_technologies(project_id);
CREATE INDEX IF NOT EXISTS idx_side_project_features_project ON side_project_features(project_id);
CREATE INDEX IF NOT EXISTS idx_side_project_technical_details_project ON side_project_technical_details(project_id);
CREATE INDEX IF NOT EXISTS idx_side_project_images_project ON side_project_images(project_id);
CREATE INDEX IF NOT EXISTS idx_side_project_categories_display_order ON side_project_categories(display_order);

-- ============================================================================
-- MAGENTO SECTION
-- ============================================================================

CREATE TABLE IF NOT EXISTS magento_module_categories (
  id              INTEGER PRIMARY KEY,
  code            TEXT UNIQUE NOT NULL,
  label           TEXT NOT NULL,
  description     TEXT,
  color           TEXT,
  icon            TEXT,
  display_order   INTEGER DEFAULT 0,
  created_at      TEXT DEFAULT (datetime('now')),
  updated_at      TEXT DEFAULT (datetime('now'))
);

INSERT OR IGNORE INTO magento_module_categories (code, label, description, color, icon, display_order) VALUES
('production', 'Production', 'Modules currently in production', 'green', 'fas fa-check-circle', 1),
('in-development', 'In Development', 'Modules currently being developed', 'orange', 'fas fa-code', 2),
('future-plans', 'Future Plans', 'Planned modules for future development', 'blue', 'fas fa-lightbulb', 3);

CREATE TABLE IF NOT EXISTS magento_modules (
  id              INTEGER PRIMARY KEY,
  category_id     INTEGER REFERENCES magento_module_categories(id) ON DELETE RESTRICT,
  title           TEXT NOT NULL,
  slug            TEXT UNIQUE,
  version         TEXT,
  description     TEXT,
  status          TEXT DEFAULT 'in development',
  metrics         TEXT,
  posted_date     TEXT,
  revised_date    TEXT,
  stats           TEXT,
  created_at      TEXT DEFAULT (datetime('now')),
  updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS magento_module_technologies (
  id              INTEGER PRIMARY KEY,
  module_id       INTEGER REFERENCES magento_modules(id) ON DELETE CASCADE,
  name            TEXT NOT NULL,
  icon            TEXT,
  display_order   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS magento_module_features (
  id              INTEGER PRIMARY KEY,
  module_id       INTEGER REFERENCES magento_modules(id) ON DELETE CASCADE,
  name            TEXT NOT NULL,
  description     TEXT,
  icon            TEXT,
  display_order   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS magento_module_technical_details (
  id              INTEGER PRIMARY KEY,
  module_id       INTEGER REFERENCES magento_modules(id) ON DELETE CASCADE,
  title           TEXT NOT NULL,
  description     TEXT NOT NULL,
  display_order   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS magento_module_images (
  id              INTEGER PRIMARY KEY,
  module_id       INTEGER REFERENCES magento_modules(id) ON DELETE CASCADE,
  url             TEXT NOT NULL,
  alt             TEXT,
  width           INTEGER,
  height          INTEGER,
  is_cover        INTEGER DEFAULT 0,
  display_order   INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_magento_modules_category ON magento_modules(category_id);
CREATE INDEX IF NOT EXISTS idx_magento_modules_slug ON magento_modules(slug);
CREATE INDEX IF NOT EXISTS idx_magento_modules_status ON magento_modules(status);
CREATE INDEX IF NOT EXISTS idx_magento_modules_posted_date ON magento_modules(posted_date);
CREATE INDEX IF NOT EXISTS idx_magento_modules_revised_date ON magento_modules(revised_date);
CREATE INDEX IF NOT EXISTS idx_magento_module_technologies_module ON magento_module_technologies(module_id);
CREATE INDEX IF NOT EXISTS idx_magento_module_features_module ON magento_module_features(module_id);
CREATE INDEX IF NOT EXISTS idx_magento_module_technical_details_module ON magento_module_technical_details(module_id);
CREATE INDEX IF NOT EXISTS idx_magento_module_images_module ON magento_module_images(module_id);
CREATE INDEX IF NOT EXISTS idx_magento_module_categories_display_order ON magento_module_categories(display_order);

-- ============================================================================
-- PHOTOGRAPHY SECTION
-- ============================================================================

CREATE TABLE IF NOT EXISTS photography_categories (
  id              INTEGER PRIMARY KEY,
  code            TEXT UNIQUE NOT NULL,
  label           TEXT NOT NULL,
  description     TEXT,
  color           TEXT,
  icon            TEXT,
  display_order   INTEGER DEFAULT 0,
  created_at      TEXT DEFAULT (datetime('now')),
  updated_at      TEXT DEFAULT (datetime('now'))
);

INSERT OR IGNORE INTO photography_categories (code, label, description, color, icon, display_order) VALUES
('wine', 'Wine', 'Wine photography', 'purple', 'fas fa-wine-glass', 1),
('landscape', 'Landscape', 'Landscape photography', 'blue', 'fas fa-mountain', 2),
('products', 'Products', 'Product photography', 'green', 'fas fa-box', 3);

CREATE TABLE IF NOT EXISTS photography (
  id              INTEGER PRIMARY KEY,
  category_id     INTEGER REFERENCES photography_categories(id) ON DELETE RESTRICT,
  photo_name      TEXT NOT NULL,
  photo_description TEXT,
  location        TEXT,
  year            TEXT,
  tags            TEXT,
  photo_details   TEXT,
  technical_details TEXT,
  image_url       TEXT,
  created_at      TEXT DEFAULT (datetime('now')),
  updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_photography_category ON photography(category_id);

-- ============================================================================
-- EXPERIENCE SECTION
-- ============================================================================

CREATE TABLE IF NOT EXISTS experience_companies (
  id              INTEGER PRIMARY KEY,
  name            TEXT NOT NULL,
  logo_url        TEXT,
  description     TEXT,
  website         TEXT,
  location        TEXT,
  sort_order      INTEGER DEFAULT 0,
  created_at      TEXT DEFAULT (datetime('now')),
  updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS experience_job_experiences (
  id                  INTEGER PRIMARY KEY,
  company_id           INTEGER REFERENCES experience_companies(id) ON DELETE RESTRICT,
  job_title            TEXT NOT NULL,
  start_date           TEXT NOT NULL,
  end_date             TEXT,
  is_current           INTEGER DEFAULT 0,
  employment_type      TEXT,
  is_remote            INTEGER DEFAULT 0,
  is_concurrent        INTEGER DEFAULT 0,
  role_overview        TEXT,
  key_achievements     TEXT,
  key_responsibilities TEXT,
  created_at          TEXT DEFAULT (datetime('now')),
  updated_at          TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS experience_job_projects (
  id                  INTEGER PRIMARY KEY,
  job_experience_id   INTEGER REFERENCES experience_job_experiences(id) ON DELETE CASCADE,
  month_year          TEXT NOT NULL,
  title               TEXT NOT NULL,
  link                TEXT,
  sort_order          INTEGER DEFAULT 0,
  created_at          TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS experience_skills_sets (
  id              INTEGER PRIMARY KEY,
  name            TEXT NOT NULL UNIQUE,
  icon            TEXT,
  description     TEXT,
  category        TEXT,
  color           TEXT,
  created_at      TEXT DEFAULT (datetime('now')),
  updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS experience_tools (
  id              INTEGER PRIMARY KEY,
  name            TEXT NOT NULL UNIQUE,
  icon            TEXT,
  created_at      TEXT DEFAULT (datetime('now')),
  updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS experience_soft_skills (
  id              INTEGER PRIMARY KEY,
  name            TEXT NOT NULL UNIQUE,
  icon            TEXT,
  created_at      TEXT DEFAULT (datetime('now')),
  updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS experience_education (
  id                  INTEGER PRIMARY KEY,
  certificate_name     TEXT NOT NULL,
  subtitle            TEXT,
  school_name         TEXT NOT NULL,
  location            TEXT,
  start_year          TEXT,
  end_year            TEXT,
  timeline_date       TEXT NOT NULL,
  description         TEXT,
  honors_memberships  TEXT,
  created_at          TEXT DEFAULT (datetime('now')),
  updated_at          TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS experience_job_experience_skills (
  job_experience_id   INTEGER NOT NULL REFERENCES experience_job_experiences(id) ON DELETE CASCADE,
  skill_id            INTEGER NOT NULL REFERENCES experience_skills_sets(id) ON DELETE CASCADE,
  PRIMARY KEY (job_experience_id, skill_id)
);

CREATE TABLE IF NOT EXISTS experience_job_experience_tools (
  job_experience_id   INTEGER NOT NULL REFERENCES experience_job_experiences(id) ON DELETE CASCADE,
  tool_id             INTEGER NOT NULL REFERENCES experience_tools(id) ON DELETE CASCADE,
  PRIMARY KEY (job_experience_id, tool_id)
);

CREATE TABLE IF NOT EXISTS experience_job_experience_soft_skills (
  job_experience_id   INTEGER NOT NULL REFERENCES experience_job_experiences(id) ON DELETE CASCADE,
  soft_skill_id       INTEGER NOT NULL REFERENCES experience_soft_skills(id) ON DELETE CASCADE,
  PRIMARY KEY (job_experience_id, soft_skill_id)
);

CREATE INDEX IF NOT EXISTS idx_experience_job_experiences_company ON experience_job_experiences(company_id);
CREATE INDEX IF NOT EXISTS idx_experience_job_experiences_start_date ON experience_job_experiences(start_date DESC);
CREATE INDEX IF NOT EXISTS idx_experience_job_projects_job_experience ON experience_job_projects(job_experience_id);
CREATE INDEX IF NOT EXISTS idx_experience_job_experience_skills_job ON experience_job_experience_skills(job_experience_id);
CREATE INDEX IF NOT EXISTS idx_experience_job_experience_skills_skill ON experience_job_experience_skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_experience_job_experience_tools_job ON experience_job_experience_tools(job_experience_id);
CREATE INDEX IF NOT EXISTS idx_experience_job_experience_tools_tool ON experience_job_experience_tools(tool_id);
CREATE INDEX IF NOT EXISTS idx_experience_job_experience_soft_skills_job ON experience_job_experience_soft_skills(job_experience_id);
CREATE INDEX IF NOT EXISTS idx_experience_job_experience_soft_skills_skill ON experience_job_experience_soft_skills(soft_skill_id);
CREATE INDEX IF NOT EXISTS idx_experience_education_timeline_date ON experience_education(timeline_date DESC);

CREATE TABLE IF NOT EXISTS experience_certifications (
  id              INTEGER PRIMARY KEY,
  name            TEXT NOT NULL,
  issuer          TEXT NOT NULL,
  status          TEXT NOT NULL DEFAULT 'completed',
  issued_date     TEXT,
  notes           TEXT,
  sort_order      INTEGER DEFAULT 0,
  created_at      TEXT DEFAULT (datetime('now')),
  updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_experience_certifications_sort ON experience_certifications(sort_order);

-- ============================================================================
-- CMS SECTION
-- ============================================================================

CREATE TABLE IF NOT EXISTS cms_blocks (
    id              INTEGER PRIMARY KEY,
    block_id        TEXT UNIQUE NOT NULL,
    title           TEXT NOT NULL,
    content         TEXT NOT NULL,
    content_format  TEXT DEFAULT 'html',
    description     TEXT,
    is_active       INTEGER DEFAULT 1,
    sort_order      INTEGER DEFAULT 0,
    image           TEXT,
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now')),
    image_position  TEXT DEFAULT 'right',
    image_description TEXT,
    gallery_images  TEXT
);

CREATE TABLE IF NOT EXISTS cms_site_settings (
    id              INTEGER PRIMARY KEY,
    setting_key     TEXT UNIQUE NOT NULL,
    setting_value   TEXT NOT NULL,
    setting_type    TEXT DEFAULT 'text',
    description     TEXT,
    updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS cms_contact_info (
    id                      INTEGER PRIMARY KEY,
    field_name              TEXT UNIQUE NOT NULL,
    label                   TEXT NOT NULL,
    value                   TEXT NOT NULL,
    field_type              TEXT DEFAULT 'text',
    icon                    TEXT,
    is_public               INTEGER DEFAULT 1,
    sort_order              INTEGER DEFAULT 0,
    updated_at              TEXT DEFAULT (datetime('now')),
    description             TEXT,
    show_in_get_in_touch    INTEGER DEFAULT 0,
    get_in_touch_title      TEXT,
    get_in_touch_description TEXT
);

INSERT OR IGNORE INTO cms_site_settings (setting_key, setting_value, setting_type, description) VALUES
('site_name', 'Bradley R. Clampitt', 'text', 'Full name displayed in header'),
('site_titles', 'Digital Solutions Architect & Tech Leader | Magento & eCommerce Architecture | AWS & Cloud | AI-Augmented Development', 'text', 'Professional titles displayed in header'),
('site_description', 'Solutions Architect specializing in Magento Enterprise, AWS cloud infrastructure, and AI-augmented development. 21+ years of eCommerce leadership. Open to full-time salary roles - available immediately.', 'text', 'Short bio/description displayed in header');

INSERT OR IGNORE INTO cms_contact_info (field_name, label, value, field_type, icon, is_public, sort_order) VALUES
('email', 'Email', 'bradclampitt@gmail.com', 'email', 'fas fa-envelope', 1, 1),
('github', 'GitHub', 'https://github.com/bradclampitt', 'url', 'fab fa-github', 1, 2),
('linkedin', 'LinkedIn', 'https://linkedin.com/in/bclampitt', 'url', 'fab fa-linkedin', 1, 3),
('whatsapp', 'WhatsApp', 'https://wa.me/', 'url', 'fab fa-whatsapp', 0, 4),
('location', 'Location', 'United States', 'text', 'fas fa-map-marker-alt', 1, 5);

CREATE INDEX IF NOT EXISTS idx_cms_blocks_block_id ON cms_blocks(block_id);
CREATE INDEX IF NOT EXISTS idx_cms_blocks_active ON cms_blocks(is_active);
CREATE INDEX IF NOT EXISTS idx_cms_blocks_sort ON cms_blocks(sort_order);
CREATE INDEX IF NOT EXISTS idx_cms_site_settings_key ON cms_site_settings(setting_key);
CREATE INDEX IF NOT EXISTS idx_cms_contact_info_field_name ON cms_contact_info(field_name);
CREATE INDEX IF NOT EXISTS idx_cms_contact_info_public ON cms_contact_info(is_public);
CREATE INDEX IF NOT EXISTS idx_cms_contact_info_sort ON cms_contact_info(sort_order);
