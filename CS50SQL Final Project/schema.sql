-- users table
CREATE TABLE users(
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  department TEXT CHECK( department IN ('VFX','COMP') ) ,
  active BOOLEAN NOT NULL,
  role TEXT NOT NULL CHECK( role IN ('Artist','Coordinator', 'Supervisor') ) ,
  email TEXT CHECK( email LIKE '%@%' ) ,
  create_date DATE NOT NULL DEFAULT CURRENT_DATE,
  last_active_date DATE NOT NULL DEFAULT CURRENT_DATE
);
-- projects table
CREATE TABLE projects(
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  name TEXT NOT NULL,
  client TEXT NOT NULL,
  type TEXT NOT NULL CHECK( type IN ('file','series') ) ,
  fps DECIMAL(2,1) NOT NULL,
  start_date DATE NOT NULL DEFAULT CURRENT_DATE,
  end_date DATE NOT NULL DEFAULT CURRENT_DATE
);
-- shots table
CREATE TABLE shots(
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  name TEXT NOT NULL,
  project_id INTEGER NOT NULL,
  start_frame INTEGER NOT NULL DEFAULT 1001,
  end_frame INTEGER NOT NULL DEFAULT 1100,
  focal_length DECIMAL(5,1) NOT NULL,
  shot_start_date DATE DEFAULT CURRENT_DATE,
  shot_end_date DATE DEFAULT CURRENT_DATE,
  FOREIGN KEY (project_id) REFERENCES projects (id)
);
-- tasks table
CREATE TABLE tasks(
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  shot_id INTEGER NOT NULL,
  type TEXT  NOT NULL CHECK( type IN ('pre', 'prod', 'post') ) ,
  status TEXT NOT NULL CHECK( status IN ('ready to start', 'WIP', 'pending review', 'approve') ) ,
  assigned_user_id INTEGER,
  task_start_date DATE DEFAULT CURRENT_DATE,
  task_end_date DATE DEFAULT CURRENT_DATE,
  revision INTEGER NOT NULL DEFAULT 0,
  FOREIGN KEY (shot_id) REFERENCES shots (id),
  FOREIGN KEY (assigned_user_id) REFERENCES users (id)
);
-- comments table
CREATE TABLE comments(
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  task_id INTEGER NOT NULL,
  commenter_id INTEGER NOT NULL,
  content TEXT,
  timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  task_revision INTEGER NOT NULL DEFAULT 0,
  FOREIGN KEY (task_id) REFERENCES tasks (id),
  FOREIGN KEY (commenter_id) REFERENCES users (id)
);
-- Index the shot name.
CREATE INDEX "shotname_index" ON "shots" ("name");
-- List the tasks assigned to someone by their name as a view.
CREATE VIEW "tasklist" AS
SELECT "id" AS "task_id","shot_id","first_name","last_name","task_end_date","revision" FROM "tasks"
JOIN "users" ON "users"."id" = "tasks"."assigned_user_id";
