package com.jobapp.entity;

/**
 * The applicant tracking system a job posting lives on.
 * Each value maps to one automation adapter that knows how to fill that site's forms.
 */
public enum JobType {
    WORKDAY,
    DIGICERT,
    /** Oracle Recruiting Cloud candidate sites, e.g. JPMorgan Chase (jpmc.fa.oraclecloud.com). */
    ORACLE
}
