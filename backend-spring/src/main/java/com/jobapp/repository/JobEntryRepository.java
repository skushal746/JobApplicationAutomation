package com.jobapp.repository;

import com.jobapp.entity.JobEntry;
import com.jobapp.entity.JobEntryStatus;
import com.jobapp.entity.JobType;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface JobEntryRepository extends JpaRepository<JobEntry, Long> {

    List<JobEntry> findByJobType(JobType jobType);

    List<JobEntry> findByUserId(Long userId);

    List<JobEntry> findByUserIdOrderByCreatedAtDesc(Long userId);

    List<JobEntry> findByStatus(JobEntryStatus status);

    boolean existsByUserIdAndUrl(Long userId, String url);

    Optional<JobEntry> findByIdAndUserId(Long id, Long userId);
}
