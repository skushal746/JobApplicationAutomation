package com.jobapp.controller;

import com.jobapp.dto.CreateJobEntryRequest;
import com.jobapp.dto.UpdateJobEntryRequest;
import com.jobapp.entity.JobEntry;
import com.jobapp.entity.User;
import com.jobapp.service.JobEntryService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/job-entries")
@RequiredArgsConstructor
public class JobEntryController {

    private final JobEntryService jobEntryService;

    @PostMapping
    public ResponseEntity<JobEntry> create(@AuthenticationPrincipal User user,
                                           @Valid @RequestBody CreateJobEntryRequest request) {
        JobEntry created = jobEntryService.create(user.getId(), request);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @PatchMapping("/{id}")
    public ResponseEntity<JobEntry> update(@AuthenticationPrincipal User user,
                                           @PathVariable Long id,
                                           @Valid @RequestBody UpdateJobEntryRequest request) {
        return ResponseEntity.ok(jobEntryService.update(user.getId(), id, request));
    }
}
