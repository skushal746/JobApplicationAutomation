package com.jobapp.dto;

import com.jobapp.entity.JobType;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Data;
import org.hibernate.validator.constraints.URL;

@Data
public class CreateJobEntryRequest {

    @NotBlank
    @URL(regexp = "^https?://.*", message = "Must be a valid http or https URL")
    @Size(max = 700)
    private String url;

    @NotNull
    private JobType jobType;
}
