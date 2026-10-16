package com.jobapp.service;

import com.jobapp.dto.CreateJobEntryRequest;
import com.jobapp.dto.UpdateJobEntryRequest;
import com.jobapp.entity.JobEntry;
import com.jobapp.entity.JobEntryStatus;
import com.jobapp.entity.JobType;
import com.jobapp.repository.JobEntryRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class JobEntryService {

    private static final String DUPLICATE_MESSAGE = "You already have a job entry with this URL";

    private final JobEntryRepository jobEntryRepository;

    /**
     * Returns the user's entries, newest first. Every filter is optional.
     * from and to are inclusive calendar days applied to createdAt:
     * only from means that day onwards, only to means up to the end of that day,
     * and both means the range between them.
     */
    public List<JobEntry> search(Long userId, LocalDate from, LocalDate to,
                                 JobEntryStatus status, JobType jobType) {
        if (from != null && to != null && from.isAfter(to)) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "'from' date must not be after 'to' date");
        }

        Specification<JobEntry> spec = (root, query, cb) -> cb.equal(root.get("userId"), userId);
        if (from != null) {
            LocalDateTime start = from.atStartOfDay();
            spec = spec.and((root, query, cb) -> cb.greaterThanOrEqualTo(root.get("createdAt"), start));
        }
        if (to != null) {
            // Strictly before the next midnight, so the whole 'to' day is included.
            LocalDateTime endExclusive = to.plusDays(1).atStartOfDay();
            spec = spec.and((root, query, cb) -> cb.lessThan(root.get("createdAt"), endExclusive));
        }
        if (status != null) {
            spec = spec.and((root, query, cb) -> cb.equal(root.get("status"), status));
        }
        if (jobType != null) {
            spec = spec.and((root, query, cb) -> cb.equal(root.get("jobType"), jobType));
        }

        return jobEntryRepository.findAll(spec, Sort.by(Sort.Direction.DESC, "createdAt"));
    }

    public JobEntry create(Long userId, CreateJobEntryRequest request) {
        String url = request.getUrl().trim();
        if (jobEntryRepository.existsByUserIdAndUrl(userId, url)) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, DUPLICATE_MESSAGE);
        }

        JobEntry entry = JobEntry.builder()
                .userId(userId)
                .url(url)
                .jobType(request.getJobType())
                .status(JobEntryStatus.PENDING)
                .build();

        return saveOrConflict(entry);
    }

    public JobEntry update(Long userId, Long id, UpdateJobEntryRequest request) {
        // Scoping the lookup by user means another user's entry looks the same as a missing one.
        JobEntry entry = jobEntryRepository.findByIdAndUserId(id, userId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Job entry not found"));

        if (request.getUrl() != null) {
            String url = request.getUrl().trim();
            if (!url.equals(entry.getUrl()) && jobEntryRepository.existsByUserIdAndUrl(userId, url)) {
                throw new ResponseStatusException(HttpStatus.CONFLICT, DUPLICATE_MESSAGE);
            }
            entry.setUrl(url);
        }
        if (request.getJobType() != null) {
            entry.setJobType(request.getJobType());
        }
        if (request.getStatus() != null) {
            entry.setStatus(request.getStatus());
        }

        return saveOrConflict(entry);
    }

    // The exists check above can race with a concurrent request; the unique key is the final guard.
    private JobEntry saveOrConflict(JobEntry entry) {
        try {
            return jobEntryRepository.saveAndFlush(entry);
        } catch (DataIntegrityViolationException e) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, DUPLICATE_MESSAGE, e);
        }
    }
}
