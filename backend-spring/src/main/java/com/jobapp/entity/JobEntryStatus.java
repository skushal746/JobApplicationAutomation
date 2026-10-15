package com.jobapp.entity;

/**
 * Lifecycle of a job entry as it moves through the automation pipeline.
 */
public enum JobEntryStatus {
    PENDING,
    IN_PROGRESS,
    NEEDS_REVIEW,
    SUBMITTED,
    FAILED
}
