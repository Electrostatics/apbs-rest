CREATE TABLE workflows(
    job_id VARCHAR(10),
    workflow VARCHAR(1000),
    workflow_status VARCHAR(8),
    current_task SMALLINT(4),
    task_status VARCHAR(8),
    task_params TEXT,
    task_output TEXT,
    -- task_params VARCHAR(10000),
    -- task_output VARCHAR(10000),

    PRIMARY KEY(job_id)
);
