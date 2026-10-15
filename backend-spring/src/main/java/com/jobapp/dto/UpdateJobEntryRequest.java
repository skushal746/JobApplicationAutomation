package com.jobapp.dto;

import com.jobapp.entity.JobEntryStatus;
import com.jobapp.entity.JobType;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.Data;
import org.hibernate.validator.constraints.URL;

/**
 * Partial update: only the fields that are present (non-null) are changed.
 */
@Data
public class UpdateJobEntryRequest {

    @URL(regexp = "^https?://.*", message = "Must be a valid http or https URL")
    @Pattern(regexp = ".*\\S.*", message = "Must not be blank")
    @Size(max = 700)
    private String url;

    private JobType jobType;

    private JobEntryStatus status;
}
