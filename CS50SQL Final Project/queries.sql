-- Find the shots assigned to someone by their name in the "tasklist" view.
SELECT "shot_id" FROM "tasklist"
WHERE "first_name" = "weihsiang"
AND "last_name" = "chen";

-- Find someone's tasks that are due.
SELECT "task_end_date" FROM "tasklist"
WHERE "first_name" = "weihsiang"
AND "last_name" = "chen"
AND CURRENT_DATE > "task_end_date";

-- Find the comment on the latest revision of someone's task.
WITH "weihsiang_tasklist" AS (
    SELECT "task_id","revision" FROM "tasklist"
    WHERE "first_name" = "weihsiang"
    AND "last_name" = "chen"
)
SELECT "content" FROM "comments"
WHERE "comments"."task_id" IN (
    SELECT "task_id" FROM "weihsiang_tasklist"
)
AND "task_revision" = (
    SELECT "revision" FROM "weihsiang_tasklist"
)
